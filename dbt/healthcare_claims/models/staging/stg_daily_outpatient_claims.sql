select
    desynpuf_id as beneficiary_id,
    clm_id as claim_id,
    segment as claim_segment,
    'outpatient' as claim_type,
    'daily_synthetic' as source_system,

    nullif(clm_from_dt, '')::date as claim_start_date,
    nullif(clm_thru_dt, '')::date as claim_end_date,

    prvdr_num as provider_id,

    clm_pmt_amt::numeric as claim_payment_amount,
    nch_prmry_pyr_clm_pd_amt::numeric as primary_payer_claim_paid_amount,
    nch_bene_blood_ddctbl_lblty_am::numeric as blood_deductible_liability_amount,
    nch_bene_ptb_ddctbl_amt::numeric as part_b_deductible_amount,
    nch_bene_ptb_coinsrnc_amt::numeric as part_b_coinsurance_amount,

    at_physn_npi as attending_physician_npi,
    op_physn_npi as operating_physician_npi,
    ot_physn_npi as other_physician_npi,

    admtng_icd9_dgns_cd as admitting_diagnosis_code,
    icd9_dgns_cd_1 as primary_diagnosis_code,
    icd9_dgns_cd_2 as diagnosis_code_2,
    icd9_dgns_cd_3 as diagnosis_code_3,
    icd9_dgns_cd_4 as diagnosis_code_4,
    icd9_dgns_cd_5 as diagnosis_code_5,
    icd9_dgns_cd_6 as diagnosis_code_6,
    icd9_dgns_cd_7 as diagnosis_code_7,
    icd9_dgns_cd_8 as diagnosis_code_8,
    icd9_dgns_cd_9 as diagnosis_code_9,
    icd9_dgns_cd_10 as diagnosis_code_10,

    icd9_prcdr_cd_1 as procedure_code_1,
    icd9_prcdr_cd_2 as procedure_code_2,
    icd9_prcdr_cd_3 as procedure_code_3,
    icd9_prcdr_cd_4 as procedure_code_4,
    icd9_prcdr_cd_5 as procedure_code_5,
    icd9_prcdr_cd_6 as procedure_code_6,

    hcpcs_cd_1 as hcpcs_code_1,
    hcpcs_cd_2 as hcpcs_code_2,
    hcpcs_cd_3 as hcpcs_code_3,
    hcpcs_cd_4 as hcpcs_code_4,
    hcpcs_cd_5 as hcpcs_code_5,

    feed_date,
    source_file_name,
    ingested_at

from {{ source('bronze', 'daily_outpatient_claims') }}