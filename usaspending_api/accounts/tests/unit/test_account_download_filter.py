import pytest

from model_mommy import mommy

from usaspending_api.accounts.models import AppropriationAccountBalances, TreasuryAppropriationAccount
from usaspending_api.accounts.v2.filters.account_download import account_download_filter
from usaspending_api.awards.models import FinancialAccountsByAwards
from usaspending_api.financial_activities.models import FinancialAccountsByProgramActivityObjectClass
from usaspending_api.references.models import ToptierAgency


@pytest.mark.django_db
def test_fyq_filter():
    """ Ensure the fiscal year and quarter filter is working """
    # Create TAS models
    tas1 = mommy.make('accounts.TreasuryAppropriationAccount')
    tas2 = mommy.make('accounts.TreasuryAppropriationAccount')

    # Create file A models
    mommy.make('accounts.AppropriationAccountBalances', treasury_account_identifier=tas1,
               reporting_period_start='1699-10-01', reporting_period_end='1699-12-31')
    mommy.make('accounts.AppropriationAccountBalances', treasury_account_identifier=tas2,
               reporting_period_start='1700-01-01', reporting_period_end='1700-03-31')

    queryset = account_download_filter('account_balances', AppropriationAccountBalances, {
        'fy': 1700,
        'quarter': 1
    })
    assert queryset.count() == 1


@pytest.mark.django_db
def test_federal_account_filter():
    """ Ensure the fiscal year and quarter filter is working """
    # Create FederalAccount models
    fed_acct1 = mommy.make('accounts.FederalAccount')
    fed_acct2 = mommy.make('accounts.FederalAccount')

    # Create TAS models
    tas1 = mommy.make('accounts.TreasuryAppropriationAccount', federal_account=fed_acct1)
    tas2 = mommy.make('accounts.TreasuryAppropriationAccount', federal_account=fed_acct2)

    # Create file A models
    mommy.make('accounts.AppropriationAccountBalances', treasury_account_identifier=tas1,
               reporting_period_start='1699-10-01', reporting_period_end='1699-12-31')
    mommy.make('accounts.AppropriationAccountBalances', treasury_account_identifier=tas2,
               reporting_period_start='1699-10-01', reporting_period_end='1699-12-31')

    queryset = account_download_filter('account_balances', AppropriationAccountBalances, {
        'federal_account': fed_acct1.id,
        'fy': 1700,
        'quarter': 1
    })
    assert queryset.count() == 1


@pytest.mark.django_db
def test_cgac_agency_filter():
    """ Ensure the CGAC agency filter is working """
    # Create TAS models
    tas1 = mommy.make('accounts.TreasuryAppropriationAccount', agency_id='NOT')
    tas2 = mommy.make('accounts.TreasuryAppropriationAccount', agency_id='CGC')

    # Create file B models
    mommy.make(FinancialAccountsByProgramActivityObjectClass, treasury_account_id=tas1.treasury_account_identifier,
               reporting_period_start='1699-10-01', reporting_period_end='1699-12-31')
    mommy.make(FinancialAccountsByProgramActivityObjectClass, treasury_account_id=tas2.treasury_account_identifier,
               reporting_period_start='1699-10-01', reporting_period_end='1699-12-31')

    # Create ToptierAgency models
    mommy.make(ToptierAgency, toptier_agency_id=-9999, cgac_code='CGC')
    mommy.make(ToptierAgency, toptier_agency_id=-9998, cgac_code='NOT')

    # Filter by ToptierAgency (CGAC)
    queryset = account_download_filter('program_activity_object_class', FinancialAccountsByProgramActivityObjectClass, {
        'agency': '-9999',
        'fy': 1700,
        'quarter': 1
    })
    assert queryset.count() == 1


@pytest.mark.django_db
def test_frec_agency_filter():
    """ Ensure the FREC agency filter is working """
    # Create TAS models
    tas1 = mommy.make('accounts.TreasuryAppropriationAccount', agency_id='CGC', fr_entity_code='FAKE')
    tas2 = mommy.make('accounts.TreasuryAppropriationAccount', agency_id='CGC', fr_entity_code='FREC')

    # Create file C models
    mommy.make(FinancialAccountsByAwards, treasury_account_id=tas1.treasury_account_identifier,
               reporting_period_start='1699-10-01', reporting_period_end='1699-12-31')
    mommy.make(FinancialAccountsByAwards, treasury_account_id=tas2.treasury_account_identifier,
               reporting_period_start='1699-10-01', reporting_period_end='1699-12-31')

    # Create ToptierAgency models
    mommy.make(ToptierAgency, toptier_agency_id=-9999, cgac_code='FREC')
    mommy.make(ToptierAgency, toptier_agency_id=-9998, cgac_code='FAKE')
    mommy.make(ToptierAgency, toptier_agency_id=-9997, cgac_code='CGC')

    # Filter by ToptierAgency (FREC)
    queryset = account_download_filter('award_financial', FinancialAccountsByAwards, {
        'agency': '-9999',
        'fy': 1700,
        'quarter': 1
    })
    assert queryset.count() == 1
