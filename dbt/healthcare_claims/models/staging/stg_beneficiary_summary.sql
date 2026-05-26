select
    desynpuf_id as beneficiary_id,

    nullif(bene_birth_dt, '')::date as birth_date,
    nullif(bene_death_dt, '')::date as death_date,

    bene_sex_ident_cd as sex_code,
    bene_race_cd as race_code,
    bene_esrd_ind as esrd_indicator,
    sp_state_code as state_code,
    bene_county_cd as county_code,

    bene_hi_cvrage_tot_mons::numeric as part_a_coverage_months,
    bene_smi_cvrage_tot_mons::numeric as part_b_coverage_months,
    bene_hmo_cvrage_tot_mons::numeric as hmo_coverage_months,
    plan_cvrg_mos_num::numeric as part_d_coverage_months,

    sp_alzhdmta::integer as has_alzheimer_or_dementia,
    sp_chf::integer as has_chronic_heart_failure,
    sp_chrnkidn::integer as has_chronic_kidney_disease,
    sp_cncr::integer as has_cancer,
    sp_copd::integer as has_copd,
    sp_depressn::integer as has_depression,
    sp_diabetes::integer as has_diabetes,
    sp_ischmcht::integer as has_ischemic_heart_disease,
    sp_osteoprs::integer as has_osteoporosis,
    sp_ra_oa::integer as has_rheumatoid_or_osteoarthritis,
    sp_strketia::integer as has_stroke_or_tia,

    medreimb_ip::numeric as medicare_reimbursement_inpatient,
    benres_ip::numeric as beneficiary_responsibility_inpatient,
    pppymt_ip::numeric as primary_payer_payment_inpatient,

    medreimb_op::numeric as medicare_reimbursement_outpatient,
    benres_op::numeric as beneficiary_responsibility_outpatient,
    pppymt_op::numeric as primary_payer_payment_outpatient,

    medreimb_car::numeric as medicare_reimbursement_carrier,
    benres_car::numeric as beneficiary_responsibility_carrier,
    pppymt_car::numeric as primary_payer_payment_carrier,

    source_year,
    source_file_name,
    ingested_at

from {{ source('bronze', 'beneficiary_summary') }}