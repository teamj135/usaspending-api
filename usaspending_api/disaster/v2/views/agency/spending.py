from django.contrib.postgres.fields import ArrayField
from django.db.models import Case, DecimalField, F, IntegerField, Q, Sum, Value, When
from django.db.models.functions import Coalesce
from rest_framework.response import Response
from usaspending_api.awards.models import FinancialAccountsByAwards
from usaspending_api.common.cache_decorator import cache_response
from usaspending_api.common.helpers.generic_helper import get_pagination_metadata
from usaspending_api.disaster.v2.views.disaster_base import DisasterBase, PaginationMixin, SpendingMixin
from usaspending_api.financial_activities.models import FinancialAccountsByProgramActivityObjectClass


class SpendingByAgencyViewSet(PaginationMixin, SpendingMixin, DisasterBase):
    """ Returns disaster spending by agency. """

    endpoint_doc = "usaspending_api/api_contracts/contracts/v2/disaster/agency/spending.md"

    @cache_response()
    def post(self, request):
        if self.spending_type == "award":
            results = self.award_queryset
        else:
            results = self.total_queryset

        return Response(
            {
                "results": results.order_by(self.pagination.order_by)[
                    self.pagination.lower_limit : self.pagination.upper_limit
                ],
                "page_metadata": get_pagination_metadata(results.count(), self.pagination.limit, self.pagination.page),
            }
        )

    @property
    def total_queryset(self):
        filters = [
            Q(
                Q(obligations_incurred_by_program_object_class_cpe__gt=0)
                | Q(obligations_incurred_by_program_object_class_cpe__lt=0)
                | Q(gross_outlay_amount_by_program_object_class_cpe__gt=0)
                | Q(gross_outlay_amount_by_program_object_class_cpe__lt=0)
            ),
            Q(disaster_emergency_fund__in=self.def_codes),
            Q(treasury_account__isnull=False),
            Q(treasury_account__funding_toptier_agency__isnull=False),
            self.all_closed_defc_submissions,
        ]

        annotations = {
            "id": F("treasury_account__funding_toptier_agency"),
            "code": F("treasury_account__funding_toptier_agency__toptier_code"),
            "description": F("treasury_account__funding_toptier_agency__name"),
            # Currently, this endpoint can never have children.
            "children": Value([], output_field=ArrayField(IntegerField())),
            "count": Value(0, output_field=IntegerField()),
            "obligation": Coalesce(
                Sum(
                    Case(
                        When(
                            self.final_period_submission_query_filters,
                            then=F("obligations_incurred_by_program_object_class_cpe"),
                        ),
                        default=Value(0),
                    )
                ),
                0,
            ),
            "outlay": Coalesce(
                Sum(
                    Case(
                        When(
                            self.final_period_submission_query_filters,
                            then=F("gross_outlay_amount_by_program_object_class_cpe"),
                        ),
                        default=Value(0),
                    )
                ),
                0,
            ),
            "total_budgetary_resources": Coalesce(
                Sum("treasury_account__gtas__budget_authority_appropriation_amount_cpe"), 0
            ),
        }

        return (
            FinancialAccountsByProgramActivityObjectClass.objects.filter(*filters)
            .values(
                "treasury_account__funding_toptier_agency",
                "treasury_account__funding_toptier_agency__toptier_code",
                "treasury_account__funding_toptier_agency__name",
            )
            .annotate(**annotations)
            .values(*annotations.keys())
        )

    @property
    def award_queryset(self):
        filters = [
            Q(disaster_emergency_fund__in=self.def_codes),
            Q(treasury_account__isnull=False),
            Q(treasury_account__funding_toptier_agency__isnull=False),
            self.all_closed_defc_submissions,
        ]

        annotations = {
            "id": F("treasury_account__funding_toptier_agency"),
            "code": F("treasury_account__funding_toptier_agency__toptier_code"),
            "description": F("treasury_account__funding_toptier_agency__name"),
            # Currently, this endpoint can never have children.
            "children": Value([], output_field=ArrayField(IntegerField())),
            "count": Value(0, output_field=IntegerField()),
            "obligation": Coalesce(Sum("transaction_obligated_amount"), 0),
            "outlay": Coalesce(
                Sum(
                    Case(
                        When(self.final_period_submission_query_filters, then=F("gross_outlay_amount_by_award_cpe")),
                        default=Value(0),
                    )
                ),
                0,
            ),
            "total_budgetary_resources": Value(None, DecimalField()),  # NULL for award spending
        }

        return (
            FinancialAccountsByAwards.objects.filter(*filters)
            .values(
                "treasury_account__funding_toptier_agency",
                "treasury_account__funding_toptier_agency__toptier_code",
                "treasury_account__funding_toptier_agency__name",
            )
            .annotate(**annotations)
            .values(*annotations.keys())
        )