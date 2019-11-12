from usaspending_api.broker.helpers.award_category_helper import award_types
from usaspending_api.etl.transaction_loaders.derived_field_functions_fpds import (
    calculate_fiscal_year,
    calculate_awarding_agency,
    calculate_funding_agency,
    current_datetime,
    business_categories,
    created_at,
    updated_at,
    legal_entity_zip5,
    legal_entity_state_description,
    place_of_performance_state_code,
    place_of_performance_state_description,
    data_source,
)
from usaspending_api.etl.transaction_loaders.data_load_helpers import truncate_timestamp

# broker column name -> usaspending column name
transaction_fpds_nonboolean_columns = {
    "detached_award_procurement_id": "detached_award_procurement_id",
    "detached_award_proc_unique": "detached_award_proc_unique",
    "piid": "piid",
    "agency_id": "agency_id",
    "awarding_sub_tier_agency_c": "awarding_sub_tier_agency_c",
    "awarding_sub_tier_agency_n": "awarding_sub_tier_agency_n",
    "awarding_agency_code": "awarding_agency_code",
    "awarding_agency_name": "awarding_agency_name",
    "parent_award_id": "parent_award_id",
    "award_modification_amendme": "award_modification_amendme",
    "type_of_contract_pricing": "type_of_contract_pricing",
    "type_of_contract_pric_desc": "type_of_contract_pric_desc",
    "contract_award_type": "contract_award_type",
    "contract_award_type_desc": "contract_award_type_desc",
    "naics": "naics",
    "naics_description": "naics_description",
    "awardee_or_recipient_uniqu": "awardee_or_recipient_uniqu",
    "ultimate_parent_legal_enti": "ultimate_parent_legal_enti",
    "ultimate_parent_unique_ide": "ultimate_parent_unique_ide",
    "award_description": "award_description",
    "place_of_performance_zip4a": "place_of_performance_zip4a",
    "place_of_performance_zip5": "place_of_performance_zip5",
    "place_of_perform_zip_last4": "place_of_perform_zip_last4",
    "place_of_perform_city_name": "place_of_perform_city_name",
    "place_of_perform_county_co": "place_of_perform_county_co",
    "place_of_perform_county_na": "place_of_perform_county_na",
    "place_of_performance_congr": "place_of_performance_congr",
    "awardee_or_recipient_legal": "awardee_or_recipient_legal",
    "legal_entity_city_name": "legal_entity_city_name",
    "legal_entity_county_code": "legal_entity_county_code",
    "legal_entity_county_name": "legal_entity_county_name",
    "legal_entity_state_code": "legal_entity_state_code",
    "legal_entity_state_descrip": "legal_entity_state_descrip",
    "legal_entity_zip4": "legal_entity_zip4",
    "legal_entity_zip5": "legal_entity_zip5",
    "legal_entity_zip_last4": "legal_entity_zip_last4",
    "legal_entity_congressional": "legal_entity_congressional",
    "legal_entity_address_line1": "legal_entity_address_line1",
    "legal_entity_address_line2": "legal_entity_address_line2",
    "legal_entity_address_line3": "legal_entity_address_line3",
    "legal_entity_country_code": "legal_entity_country_code",
    "legal_entity_country_name": "legal_entity_country_name",
    "period_of_performance_star": "period_of_performance_star",
    "period_of_performance_curr": "period_of_performance_curr",
    "period_of_perf_potential_e": "period_of_perf_potential_e",
    "action_date": "action_date",
    "action_type": "action_type",
    "action_type_description": "action_type_description",
    "federal_action_obligation": "federal_action_obligation",
    "current_total_value_award": "current_total_value_award",
    "potential_total_value_awar": "potential_total_value_awar",
    "total_obligated_amount": "total_obligated_amount",
    "base_exercised_options_val": "base_exercised_options_val",
    "base_and_all_options_value": "base_and_all_options_value",
    "funding_sub_tier_agency_co": "funding_sub_tier_agency_co",
    "funding_sub_tier_agency_na": "funding_sub_tier_agency_na",
    "funding_office_code": "funding_office_code",
    "funding_office_name": "funding_office_name",
    "awarding_office_code": "awarding_office_code",
    "awarding_office_name": "awarding_office_name",
    "referenced_idv_agency_iden": "referenced_idv_agency_iden",
    "referenced_idv_agency_desc": "referenced_idv_agency_desc",
    "funding_agency_code": "funding_agency_code",
    "funding_agency_name": "funding_agency_name",
    "place_of_performance_locat": "place_of_performance_locat",
    "place_of_performance_state": "place_of_performance_state",
    "place_of_perfor_state_desc": "place_of_perfor_state_desc",
    "place_of_perform_country_c": "place_of_perform_country_c",
    "place_of_perf_country_desc": "place_of_perf_country_desc",
    "idv_type": "idv_type",
    "idv_type_description": "idv_type_description",
    "referenced_idv_type": "referenced_idv_type",
    "referenced_idv_type_desc": "referenced_idv_type_desc",
    "vendor_doing_as_business_n": "vendor_doing_as_business_n",
    "vendor_phone_number": "vendor_phone_number",
    "vendor_fax_number": "vendor_fax_number",
    "multiple_or_single_award_i": "multiple_or_single_award_i",
    "multiple_or_single_aw_desc": "multiple_or_single_aw_desc",
    "referenced_mult_or_single": "referenced_mult_or_single",
    "referenced_mult_or_si_desc": "referenced_mult_or_si_desc",
    "type_of_idc": "type_of_idc",
    "type_of_idc_description": "type_of_idc_description",
    "a_76_fair_act_action": "a_76_fair_act_action",
    "a_76_fair_act_action_desc": "a_76_fair_act_action_desc",
    "dod_claimant_program_code": "dod_claimant_program_code",
    "dod_claimant_prog_cod_desc": "dod_claimant_prog_cod_desc",
    "clinger_cohen_act_planning": "clinger_cohen_act_planning",
    "clinger_cohen_act_pla_desc": "clinger_cohen_act_pla_desc",
    "commercial_item_acquisitio": "commercial_item_acquisitio",
    "commercial_item_acqui_desc": "commercial_item_acqui_desc",
    "commercial_item_test_progr": "commercial_item_test_progr",
    "commercial_item_test_desc": "commercial_item_test_desc",
    "consolidated_contract": "consolidated_contract",
    "consolidated_contract_desc": "consolidated_contract_desc",
    "contingency_humanitarian_o": "contingency_humanitarian_o",
    "contingency_humanitar_desc": "contingency_humanitar_desc",
    "contract_bundling": "contract_bundling",
    "contract_bundling_descrip": "contract_bundling_descrip",
    "contract_financing": "contract_financing",
    "contract_financing_descrip": "contract_financing_descrip",
    "contracting_officers_deter": "contracting_officers_deter",
    "contracting_officers_desc": "contracting_officers_desc",
    "cost_accounting_standards": "cost_accounting_standards",
    "cost_accounting_stand_desc": "cost_accounting_stand_desc",
    "cost_or_pricing_data": "cost_or_pricing_data",
    "cost_or_pricing_data_desc": "cost_or_pricing_data_desc",
    "country_of_product_or_serv": "country_of_product_or_serv",
    "country_of_product_or_desc": "country_of_product_or_desc",
    "construction_wage_rate_req": "construction_wage_rate_req",
    "construction_wage_rat_desc": "construction_wage_rat_desc",
    "evaluated_preference": "evaluated_preference",
    "evaluated_preference_desc": "evaluated_preference_desc",
    "extent_competed": "extent_competed",
    "extent_compete_description": "extent_compete_description",
    "fed_biz_opps": "fed_biz_opps",
    "fed_biz_opps_description": "fed_biz_opps_description",
    "foreign_funding": "foreign_funding",
    "foreign_funding_desc": "foreign_funding_desc",
    "government_furnished_prope": "government_furnished_prope",
    "government_furnished_desc": "government_furnished_desc",
    "information_technology_com": "information_technology_com",
    "information_technolog_desc": "information_technolog_desc",
    "interagency_contracting_au": "interagency_contracting_au",
    "interagency_contract_desc": "interagency_contract_desc",
    "local_area_set_aside": "local_area_set_aside",
    "local_area_set_aside_desc": "local_area_set_aside_desc",
    "major_program": "major_program",
    "purchase_card_as_payment_m": "purchase_card_as_payment_m",
    "purchase_card_as_paym_desc": "purchase_card_as_paym_desc",
    "multi_year_contract": "multi_year_contract",
    "multi_year_contract_desc": "multi_year_contract_desc",
    "national_interest_action": "national_interest_action",
    "national_interest_desc": "national_interest_desc",
    "number_of_actions": "number_of_actions",
    "number_of_offers_received": "number_of_offers_received",
    "other_statutory_authority": "other_statutory_authority",
    "performance_based_service": "performance_based_service",
    "performance_based_se_desc": "performance_based_se_desc",
    "place_of_manufacture": "place_of_manufacture",
    "place_of_manufacture_desc": "place_of_manufacture_desc",
    "price_evaluation_adjustmen": "price_evaluation_adjustmen",
    "product_or_service_code": "product_or_service_code",
    "product_or_service_co_desc": "product_or_service_co_desc",
    "program_acronym": "program_acronym",
    "other_than_full_and_open_c": "other_than_full_and_open_c",
    "other_than_full_and_o_desc": "other_than_full_and_o_desc",
    "recovered_materials_sustai": "recovered_materials_sustai",
    "recovered_materials_s_desc": "recovered_materials_s_desc",
    "research": "research",
    "research_description": "research_description",
    "sea_transportation": "sea_transportation",
    "sea_transportation_desc": "sea_transportation_desc",
    "labor_standards": "labor_standards",
    "labor_standards_descrip": "labor_standards_descrip",
    "solicitation_identifier": "solicitation_identifier",
    "solicitation_procedures": "solicitation_procedures",
    "solicitation_procedur_desc": "solicitation_procedur_desc",
    "fair_opportunity_limited_s": "fair_opportunity_limited_s",
    "fair_opportunity_limi_desc": "fair_opportunity_limi_desc",
    "subcontracting_plan": "subcontracting_plan",
    "subcontracting_plan_desc": "subcontracting_plan_desc",
    "program_system_or_equipmen": "program_system_or_equipmen",
    "program_system_or_equ_desc": "program_system_or_equ_desc",
    "type_set_aside": "type_set_aside",
    "type_set_aside_description": "type_set_aside_description",
    "epa_designated_product": "epa_designated_product",
    "epa_designated_produc_desc": "epa_designated_produc_desc",
    "materials_supplies_article": "materials_supplies_article",
    "materials_supplies_descrip": "materials_supplies_descrip",
    "transaction_number": "transaction_number",
    "sam_exception": "sam_exception",
    "sam_exception_description": "sam_exception_description",
    "referenced_idv_modificatio": "referenced_idv_modificatio",
    "undefinitized_action": "undefinitized_action",
    "undefinitized_action_desc": "undefinitized_action_desc",
    "domestic_or_foreign_entity": "domestic_or_foreign_entity",
    "domestic_or_foreign_e_desc": "domestic_or_foreign_e_desc",
    "annual_revenue": "annual_revenue",
    "division_name": "division_name",
    "division_number_or_office": "division_number_or_office",
    "number_of_employees": "number_of_employees",
    "vendor_alternate_name": "vendor_alternate_name",
    "vendor_alternate_site_code": "vendor_alternate_site_code",
    "vendor_enabled": "vendor_enabled",
    "vendor_legal_org_name": "vendor_legal_org_name",
    "vendor_location_disabled_f": "vendor_location_disabled_f",
    "vendor_site_code": "vendor_site_code",
    "pulled_from": "pulled_from",
    "last_modified": "last_modified",
    "initial_report_date": "initial_report_date",
    "referenced_idv_agency_name": "referenced_idv_agency_name",
    "award_or_idv_flag": "award_or_idv_flag",
    "place_of_perform_country_n": "place_of_perform_country_n",
    "place_of_perform_state_nam": "place_of_perform_state_nam",
    "cage_code": "cage_code",
    "inherently_government_desc": "inherently_government_desc",
    "inherently_government_func": "inherently_government_func",
    "organizational_type": "organizational_type",
    "unique_award_key": "unique_award_key",
    "high_comp_officer1_amount": "officer_1_amount",
    "high_comp_officer1_full_na": "officer_1_name",
    "high_comp_officer2_amount": "officer_2_amount",
    "high_comp_officer2_full_na": "officer_2_name",
    "high_comp_officer3_amount": "officer_3_amount",
    "high_comp_officer3_full_na": "officer_3_name",
    "high_comp_officer4_amount": "officer_4_amount",
    "high_comp_officer4_full_na": "officer_4_name",
    "high_comp_officer5_amount": "officer_5_amount",
    "high_comp_officer5_full_na": "officer_5_name",
    "solicitation_date": "solicitation_date",
}

transaction_fpds_boolean_columns = {
    "small_business_competitive": "small_business_competitive",
    "city_local_government": "city_local_government",
    "county_local_government": "county_local_government",
    "inter_municipal_local_gove": "inter_municipal_local_gove",
    "local_government_owned": "local_government_owned",
    "municipality_local_governm": "municipality_local_governm",
    "school_district_local_gove": "school_district_local_gove",
    "township_local_government": "township_local_government",
    "us_state_government": "us_state_government",
    "us_federal_government": "us_federal_government",
    "federal_agency": "federal_agency",
    "federally_funded_research": "federally_funded_research",
    "us_tribal_government": "us_tribal_government",
    "foreign_government": "foreign_government",
    "community_developed_corpor": "community_developed_corpor",
    "labor_surplus_area_firm": "labor_surplus_area_firm",
    "corporate_entity_not_tax_e": "corporate_entity_not_tax_e",
    "corporate_entity_tax_exemp": "corporate_entity_tax_exemp",
    "partnership_or_limited_lia": "partnership_or_limited_lia",
    "sole_proprietorship": "sole_proprietorship",
    "small_agricultural_coopera": "small_agricultural_coopera",
    "international_organization": "international_organization",
    "us_government_entity": "us_government_entity",
    "emerging_small_business": "emerging_small_business",
    "c8a_program_participant": "c8a_program_participant",
    "sba_certified_8_a_joint_ve": "sba_certified_8_a_joint_ve",
    "dot_certified_disadvantage": "dot_certified_disadvantage",
    "self_certified_small_disad": "self_certified_small_disad",
    "historically_underutilized": "historically_underutilized",
    "small_disadvantaged_busine": "small_disadvantaged_busine",
    "the_ability_one_program": "the_ability_one_program",
    "historically_black_college": "historically_black_college",
    "c1862_land_grant_college": "c1862_land_grant_college",
    "c1890_land_grant_college": "c1890_land_grant_college",
    "c1994_land_grant_college": "c1994_land_grant_college",
    "minority_institution": "minority_institution",
    "private_university_or_coll": "private_university_or_coll",
    "school_of_forestry": "school_of_forestry",
    "state_controlled_instituti": "state_controlled_instituti",
    "tribal_college": "tribal_college",
    "veterinary_college": "veterinary_college",
    "educational_institution": "educational_institution",
    "alaskan_native_servicing_i": "alaskan_native_servicing_i",
    "community_development_corp": "community_development_corp",
    "native_hawaiian_servicing": "native_hawaiian_servicing",
    "domestic_shelter": "domestic_shelter",
    "manufacturer_of_goods": "manufacturer_of_goods",
    "hospital_flag": "hospital_flag",
    "veterinary_hospital": "veterinary_hospital",
    "hispanic_servicing_institu": "hispanic_servicing_institu",
    "foundation": "foundation",
    "woman_owned_business": "woman_owned_business",
    "minority_owned_business": "minority_owned_business",
    "women_owned_small_business": "women_owned_small_business",
    "economically_disadvantaged": "economically_disadvantaged",
    "joint_venture_women_owned": "joint_venture_women_owned",
    "joint_venture_economically": "joint_venture_economically",
    "veteran_owned_business": "veteran_owned_business",
    "service_disabled_veteran_o": "service_disabled_veteran_o",
    "contracts": "contracts",
    "grants": "grants",
    "receives_contracts_and_gra": "receives_contracts_and_gra",
    "airport_authority": "airport_authority",
    "council_of_governments": "council_of_governments",
    "housing_authorities_public": "housing_authorities_public",
    "interstate_entity": "interstate_entity",
    "planning_commission": "planning_commission",
    "port_authority": "port_authority",
    "transit_authority": "transit_authority",
    "subchapter_s_corporation": "subchapter_s_corporation",
    "limited_liability_corporat": "limited_liability_corporat",
    "foreign_owned_and_located": "foreign_owned_and_located",
    "american_indian_owned_busi": "american_indian_owned_busi",
    "alaskan_native_owned_corpo": "alaskan_native_owned_corpo",
    "indian_tribe_federally_rec": "indian_tribe_federally_rec",
    "native_hawaiian_owned_busi": "native_hawaiian_owned_busi",
    "tribally_owned_business": "tribally_owned_business",
    "asian_pacific_american_own": "asian_pacific_american_own",
    "black_american_owned_busin": "black_american_owned_busin",
    "hispanic_american_owned_bu": "hispanic_american_owned_bu",
    "native_american_owned_busi": "native_american_owned_busi",
    "subcontinent_asian_asian_i": "subcontinent_asian_asian_i",
    "other_minority_owned_busin": "other_minority_owned_busin",
    "for_profit_organization": "for_profit_organization",
    "nonprofit_organization": "nonprofit_organization",
    "other_not_for_profit_organ": "other_not_for_profit_organ",
    "us_local_government": "us_local_government",
}

transaction_fpds_functions = {
    "ordering_period_end_date": lambda broker: truncate_timestamp(broker["ordering_period_end_date"]),
    "action_date": lambda broker: truncate_timestamp(broker["action_date"]),
    "initial_report_date": lambda broker: truncate_timestamp(broker["initial_report_date"]),
    "solicitation_date": lambda broker: truncate_timestamp(broker["solicitation_date"]),
    "created_at": created_at,
    "updated_at": updated_at,
}

# broker column name -> usaspending column name
transaction_normalized_nonboolean_columns = {
    "period_of_performance_star": "period_of_performance_start_date",
    "period_of_performance_curr": "period_of_performance_current_end_date",
    "action_type": "action_type",
    "action_type_description": "action_type_description",
    "federal_action_obligation": "federal_action_obligation",
    "award_description": "description",
    "last_modified": "last_modified_date",
    "award_modification_amendme": "modification_number",
    "unique_award_key": "unique_award_key",
    "detached_award_proc_unique": "transaction_unique_id",
}

# usaspending column name -> derivation function
transaction_normalized_functions = {
    "type": lambda broker: award_types(broker)[0],
    "type_description": lambda broker: award_types(broker)[1],
    "is_fpds": lambda broker: True,
    "usaspending_unique_transaction_id": lambda broker: None,  # likely obsolete
    "original_loan_subsidy_cost": lambda broker: None,  # FABS only
    "face_value_loan_guarantee": lambda broker: None,  # FABS only
    "drv_potential_total_award_value_amount_adjustment": lambda broker: None,  # ?
    "drv_current_total_award_value_amount_adjustment": lambda broker: None,  # ?
    "drv_award_transaction_usaspend": lambda broker: None,  # ?
    "certified_date": lambda broker: None,  # ?
    "fiscal_year": calculate_fiscal_year,
    "awarding_agency_id": calculate_awarding_agency,
    "funding_agency_id": calculate_funding_agency,
    "funding_amount": lambda broker: None,
    "non_federal_funding_amount": lambda broker: None,  # FABS only
    "create_date": current_datetime,  # Data loader won't add this value if it's an update
    "update_date": current_datetime,
    "action_date": lambda broker: truncate_timestamp(broker["action_date"]),
}

# broker column name -> usaspending column name
legal_entity_nonboolean_columns = {
    "awardee_or_recipient_legal": "recipient_name",
    "vendor_doing_as_business_n": "vendor_doing_as_business_name",
    "vendor_phone_number": "vendor_phone_number",
    "vendor_fax_number": "vendor_fax_number",
    "awardee_or_recipient_uniqu": "recipient_unique_id",
    "ultimate_parent_legal_enti": "parent_recipient_name",
    "ultimate_parent_unique_ide": "parent_recipient_unique_id",
    "limited_liability_corporat": "limited_liability_corporation",
    "sole_proprietorship": "sole_proprietorship",
    "partnership_or_limited_lia": "partnership_or_limited_liability_partnership",
    "foundation": "foundation",
    "for_profit_organization": "for_profit_organization",
    "nonprofit_organization": "nonprofit_organization",
    "corporate_entity_tax_exemp": "corporate_entity_tax_exempt",
    "corporate_entity_not_tax_e": "corporate_entity_not_tax_exempt",
    "other_not_for_profit_organ": "other_not_for_profit_organization",
    "sam_exception": "sam_exception",
    "undefinitized_action": "undefinitized_action",
    "domestic_or_foreign_entity": "domestic_or_foreign_entity",
    "domestic_or_foreign_e_desc": "domestic_or_foreign_entity_description",
    "division_name": "division_name",
    "division_number_or_office": "division_number",
    "detached_award_proc_unique": "transaction_unique_id",
}

legal_entity_boolean_columns = {
    "city_local_government": "city_local_government",
    "county_local_government": "county_local_government",
    "inter_municipal_local_gove": "inter_municipal_local_government",
    "local_government_owned": "local_government_owned",
    "municipality_local_governm": "municipality_local_government",
    "school_district_local_gove": "school_district_local_government",
    "township_local_government": "township_local_government",
    "us_state_government": "us_state_government",
    "us_federal_government": "us_federal_government",
    "federal_agency": "federal_agency",
    "federally_funded_research": "federally_funded_research_and_development_corp",
    "us_tribal_government": "us_tribal_government",
    "foreign_government": "foreign_government",
    "community_developed_corpor": "community_developed_corporation_owned_firm",
    "labor_surplus_area_firm": "labor_surplus_area_firm",
    "small_agricultural_coopera": "small_agricultural_cooperative",
    "international_organization": "international_organization",
    "us_government_entity": "us_government_entity",
    "emerging_small_business": "emerging_small_business",
    "c8a_program_participant": "8a_program_participant",
    "sba_certified_8_a_joint_ve": "sba_certified_8a_joint_venture",
    "dot_certified_disadvantage": "dot_certified_disadvantage",
    "subchapter_s_corporation": "subchapter_scorporation",
    "self_certified_small_disad": "self_certified_small_disadvantaged_business",
    "historically_underutilized": "historically_underutilized_business_zone",
    "small_disadvantaged_busine": "small_disadvantaged_business",
    "the_ability_one_program": "the_ability_one_program",
    "historically_black_college": "historically_black_college",
    "c1862_land_grant_college": "1862_land_grant_college",
    "c1890_land_grant_college": "1890_land_grant_college",
    "c1994_land_grant_college": "1994_land_grant_college",
    "minority_institution": "minority_institution",
    "private_university_or_coll": "private_university_or_college",
    "school_of_forestry": "school_of_forestry",
    "state_controlled_instituti": "state_controlled_institution_of_higher_learning",
    "tribal_college": "tribal_college",
    "veterinary_college": "veterinary_college",
    "educational_institution": "educational_institution",
    "alaskan_native_servicing_i": "alaskan_native_servicing_institution",
    "community_development_corp": "community_development_corporation",
    "native_hawaiian_servicing": "native_hawaiian_servicing_institution",
    "domestic_shelter": "domestic_shelter",
    "manufacturer_of_goods": "manufacturer_of_goods",
    "hospital_flag": "hospital_flag",
    "veterinary_hospital": "veterinary_hospital",
    "hispanic_servicing_institu": "hispanic_servicing_institution",
    "woman_owned_business": "woman_owned_business",
    "minority_owned_business": "minority_owned_business",
    "women_owned_small_business": "women_owned_small_business",
    "economically_disadvantaged": "economically_disadvantaged_women_owned_small_business",
    "joint_venture_women_owned": "joint_venture_women_owned_small_business",
    "joint_venture_economically": "joint_venture_economic_disadvantaged_women_owned_small_bus",
    "veteran_owned_business": "veteran_owned_business",
    "service_disabled_veteran_o": "service_disabled_veteran_owned_business",
    "contracts": "contracts",
    "grants": "grants",
    "receives_contracts_and_gra": "receives_contracts_and_grants",
    "airport_authority": "airport_authority",
    "council_of_governments": "council_of_governments",
    "housing_authorities_public": "housing_authorities_public_tribal",
    "interstate_entity": "interstate_entity",
    "planning_commission": "planning_commission",
    "port_authority": "port_authority",
    "transit_authority": "transit_authority",
    "foreign_owned_and_located": "foreign_owned_and_located",
    "american_indian_owned_busi": "american_indian_owned_business",
    "alaskan_native_owned_corpo": "alaskan_native_owned_corporation_or_firm",
    "indian_tribe_federally_rec": "indian_tribe_federally_recognized",
    "native_hawaiian_owned_busi": "native_hawaiian_owned_business",
    "tribally_owned_business": "tribally_owned_business",
    "asian_pacific_american_own": "asian_pacific_american_owned_business",
    "black_american_owned_busin": "black_american_owned_business",
    "hispanic_american_owned_bu": "hispanic_american_owned_business",
    "native_american_owned_busi": "native_american_owned_business",
    "subcontinent_asian_asian_i": "subcontinent_asian_asian_indian_american_owned_business",
    "other_minority_owned_busin": "other_minority_owned_business",
    "us_local_government": "us_local_government",
}

# usaspending column name -> derivation function
legal_entity_functions = {
    "is_fpds": lambda broker: True,
    "data_source": data_source,
    "business_types": lambda broker: None,  # FABS only
    "business_types_description": lambda broker: None,  # FABS only
    "business_categories": business_categories,
    "city_township_government": lambda broker: None,  # ?
    "special_district_government": lambda broker: None,  # ?
    "small_business": lambda broker: None,  # ?
    "small_business_description": lambda broker: None,  # ?
    "individual": lambda broker: None,  # ?
    "create_date": current_datetime,  # Data loader won't add this value if it's an update
    "update_date": current_datetime,
}

# broker column name -> usaspending column name
recipient_location_nonboolean_columns = {
    "legal_entity_country_code": "location_country_code",
    "legal_entity_country_name": "country_name",
    "legal_entity_county_code": "county_code",
    "legal_entity_state_code": "state_code",
    "legal_entity_county_name": "county_name",
    "legal_entity_congressional": "congressional_code",
    "legal_entity_city_name": "city_name",
    "legal_entity_address_line1": "address_line1",
    "legal_entity_address_line2": "address_line2",
    "legal_entity_address_line3": "address_line3",
    "legal_entity_zip4": "zip4",
    "legal_entity_zip_last4": "zip_last4",
    "detached_award_proc_unique": "transaction_unique_id",
}

# usaspending column name -> derivation function
recipient_location_functions = {
    "is_fpds": lambda broker: True,
    "data_source": data_source,
    "place_of_performance_flag": lambda broker: False,
    "recipient_flag": lambda broker: True,
    "create_date": current_datetime,  # Data loader won't add this value if it's an update
    "update_date": current_datetime,
    "zip5": legal_entity_zip5,
    "state_name": legal_entity_state_description,
}

# broker column name -> usaspending column name
place_of_performance_nonboolean_columns = {
    "place_of_perform_country_c": "location_country_code",
    "place_of_perf_country_desc": "country_name",
    "place_of_perform_county_co": "county_code",
    "place_of_perform_county_na": "county_name",
    "place_of_performance_congr": "congressional_code",
    "place_of_perform_city_name": "city_name",
    "place_of_performance_zip4a": "zip_4a",
    "place_of_performance_zip5": "zip5",
    "place_of_perform_zip_last4": "zip_last4",
    "detached_award_proc_unique": "transaction_unique_id",
}

# usaspending column name -> derivation function
place_of_performance_functions = {
    "is_fpds": lambda broker: True,
    "data_source": data_source,
    "place_of_performance_flag": lambda broker: True,
    "recipient_flag": lambda broker: False,
    "address_line1": lambda broker: None,
    "address_line2": lambda broker: None,
    "address_line3": lambda broker: None,
    "create_date": current_datetime,  # Data loader won't add this value if it's an update
    "update_date": current_datetime,
    "state_code": place_of_performance_state_code,
    "state_name": place_of_performance_state_description,
}

# broker column name -> usaspending column name
award_nonboolean_columns = {
    "unique_award_key": "generated_unique_award_id",
    "detached_award_proc_unique": "transaction_unique_id",
    "piid": "piid",
    "parent_award_id": "parent_award_piid",
}

# usaspending column name -> derivation function
award_functions = {
    "is_fpds": lambda broker: True,
    "subaward_count": lambda broker: 0,
    "awarding_agency_id": calculate_awarding_agency,
    "funding_agency_id": calculate_funding_agency,
    "data_source": lambda broker: "DBR",
    "create_date": current_datetime,  # Data loader won't add this value if it's an update
    "update_date": current_datetime,
}


def all_broker_columns():
    retval = []
    retval.extend(transaction_fpds_nonboolean_columns.keys())
    retval.extend(transaction_fpds_boolean_columns.keys())
    retval.extend(transaction_fpds_functions.keys())
    return list(set(retval))
