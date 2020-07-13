from abc import abstractmethod
from typing import List, Optional, Dict

from django.conf import settings
from django.utils.functional import cached_property
from elasticsearch_dsl import Q as ES_Q, A
from rest_framework.request import Request
from rest_framework.response import Response

from usaspending_api.awards.v2.lookups.lookups import loan_type_mapping
from usaspending_api.common.cache_decorator import cache_response
from usaspending_api.common.data_classes import Pagination
from usaspending_api.common.elasticsearch.search_wrappers import AwardSearch
from usaspending_api.common.exceptions import ForbiddenException
from usaspending_api.common.helpers.generic_helper import get_pagination_metadata
from usaspending_api.common.query_with_filters import QueryWithFilters
from usaspending_api.disaster.v2.views.disaster_base import DisasterBase, _BasePaginationMixin
from usaspending_api.search.v2.elasticsearch_helper import (
    get_scaled_sum_aggregations,
    get_number_of_unique_terms_for_awards,
)


class ElasticsearchSpendingPaginationMixin(_BasePaginationMixin):
    sum_column_mapping = {"obligation": "total_covid_obligation", "outlay": "total_covid_outlay"}
    sort_column_mapping = {
        "description": "_key",
        "count": "_count",
        **sum_column_mapping,
    }

    @cached_property
    def pagination(self):
        return self.run_models(list(self.sort_column_mapping), default_sort_column="description")


class ElasticsearchLoansPaginationMixin(_BasePaginationMixin):
    sum_column_mapping = {
        "obligation": "total_covid_obligation",
        "outlay": "total_covid_outlay",
        "face_value_of_loan": "total_loan_value",
    }
    sort_column_mapping = {
        "description": "_key",
        "count": "_count",
        **sum_column_mapping,
    }

    @cached_property
    def pagination(self):
        return self.run_models(list(self.sort_column_mapping), default_sort_column="description")


class ElasticsearchDisasterBase(DisasterBase):

    query_fields: List[str]
    agg_key: str
    is_loans: bool = False

    filter_query: ES_Q
    bucket_count: int

    pagination: Pagination  # Overwritten by a pagination mixin
    sort_column_mapping: Dict[str, str]  # Overwritten by a pagination mixin
    sum_column_mapping: Dict[str, str]  # Overwritten by a pagination mixin

    @cache_response()
    def post(self, request: Request) -> Response:
        # Handle "query" filter outside of QueryWithFilters
        query = self.filters.pop("query", None)

        # If for a loans endpoint then filter on Loans
        filters = self.filters
        if self.is_loans:
            filters.update({"award_type_codes": list(loan_type_mapping)})
        self.filter_query = QueryWithFilters.generate_awards_elasticsearch_query(filters)

        if query:
            self.filter_query.must.append(
                ES_Q("query_string", query=query, default_operator="OR", fields=self.query_fields)
            )

        # Ensure that only non-zero values are taken into consideration
        non_zero_queries = []
        for field in self.sum_column_mapping.values():
            non_zero_queries.append(ES_Q("range", **{field: {"gt": 0}}))
            non_zero_queries.append(ES_Q("range", **{field: {"lt": 0}}))
        self.filter_query.must.append(ES_Q("bool", should=non_zero_queries, minimum_should_match=1))

        self.bucket_count = get_number_of_unique_terms_for_awards(self.filter_query, f"{self.agg_key}.hash")

        results = self.query_elasticsearch()

        return Response(
            {
                "results": results[: self.pagination.limit],
                "page_metadata": get_pagination_metadata(
                    self.bucket_count, self.pagination.limit, self.pagination.page
                ),
            }
        )

    @abstractmethod
    def build_elasticsearch_result(self, response: dict) -> List[dict]:
        pass

    def build_elasticsearch_search_with_aggregations(self) -> Optional[AwardSearch]:
        """
        Using the provided ES_Q object creates an AwardSearch object with the necessary applied aggregations.
        """
        # Create the initial search using filters
        search = AwardSearch().filter(self.filter_query)

        pagination_values = {
            "from": (self.pagination.page - 1) * self.pagination.limit,
            "size": self.pagination.limit + 1,
        }
        sort_values = {"order": {self.sort_column_mapping[self.pagination.sort_key]: self.pagination.sort_order}}

        # As of writing this the value of settings.ES_ROUTING_FIELD is the only high cardinality aggregation that
        # we support. Since the Elasticsearch clusters are routed by this field we don't care to get a count of
        # unique buckets, but instead we use the upper_limit and don't allow an upper_limit > 10k.
        if self.agg_key == settings.ES_ROUTING_FIELD:
            size = self.pagination.upper_limit
            shard_size = size
            group_by_agg_key_values = {**sort_values}
            bucket_sort_values = {**pagination_values}
        else:
            if self.bucket_count == 0:
                return None
            else:
                size = self.bucket_count
                shard_size = self.bucket_count + 100
                group_by_agg_key_values = {}
                bucket_sort_values = {**pagination_values, **sort_values}

        if shard_size > 10000:
            raise ForbiddenException(
                "Current filters return too many unique items. Narrow filters to return results or use downloads."
            )

        # Define all aggregations needed to build the response
        group_by_agg_key_values.update({"field": self.agg_key, "size": size, "shard_size": shard_size})
        group_by_agg_key = A("terms", **group_by_agg_key_values)

        bucket_sort_aggregation = A("bucket_sort", **bucket_sort_values)
        sum_aggregations = {
            mapping: get_scaled_sum_aggregations(mapping, self.pagination)
            for mapping in self.sum_column_mapping.values()
        }

        # Define all aggregations needed to build the response
        search.aggs.bucket("group_by_agg_key", group_by_agg_key)
        for field, sum_aggregations in sum_aggregations.items():
            search.aggs["group_by_agg_key"].metric(field, sum_aggregations["sum_field"])
        search.aggs["group_by_agg_key"].pipeline("pagination_aggregation", bucket_sort_aggregation)

        # Set size to 0 since we don't care about documents returned
        search.update_from_dict({"size": 0})

        return search

    def query_elasticsearch(self) -> list:
        search = self.build_elasticsearch_search_with_aggregations()
        if search is None:
            return []
        response = search.handle_execute()
        results = self.build_elasticsearch_result(response.aggs.to_dict())
        return results