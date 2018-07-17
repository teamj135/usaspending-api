CREATE index IF NOT EXISTS tmp_aw_uri ON awards(uri);
CREATE index IF NOT EXISTS tmp_faba_fain_uri ON financial_accounts_by_awards(fain, uri, award_id) WHERE fain IS NOT NULL AND uri IS NOT NULL AND award_id IS NULL;
CREATE index IF NOT EXISTS tmp_faba_fain ON financial_accounts_by_awards(fain, uri, award_id) WHERE fain IS NOT NULL AND uri IS NULL AND award_id IS NULL;
CREATE index IF NOT EXISTS tmp_faba_uri ON financial_accounts_by_awards(fain, uri, award_id) WHERE fain IS NULL AND uri IS NOT NULL AND award_id IS NULL;
CREATE index IF NOT EXISTS tmp_faba_piid ON financial_accounts_by_awards(piid, award_id) WHERE piid IS NOT NULL AND award_id IS NULL;