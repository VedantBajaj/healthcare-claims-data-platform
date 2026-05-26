with ranked_beneficiaries as (
    select
        beneficiary_id,
        birth_date,
        death_date,
        sex_code,
        race_code,
        esrd_indicator,
        state_code,
        county_code,

        part_a_coverage_months,
        part_b_coverage_months,
        hmo_coverage_months,
        part_d_coverage_months,

        has_alzheimer_or_dementia,
        has_chronic_heart_failure,
        has_chronic_kidney_disease,
        has_cancer,
        has_copd,
        has_depression,
        has_diabetes,
        has_ischemic_heart_disease,
        has_osteoporosis,
        has_rheumatoid_or_osteoarthritis,
        has_stroke_or_tia,

        medicare_reimbursement_inpatient,
        beneficiary_responsibility_inpatient,
        primary_payer_payment_inpatient,

        medicare_reimbursement_outpatient,
        beneficiary_responsibility_outpatient,
        primary_payer_payment_outpatient,

        medicare_reimbursement_carrier,
        beneficiary_responsibility_carrier,
        primary_payer_payment_carrier,

        source_year,
        source_file_name,
        ingested_at,

        row_number() over (
            partition by beneficiary_id
            order by source_year desc
        ) as beneficiary_year_rank

    from {{ ref('stg_beneficiary_summary') }}
)

select
    beneficiary_id,
    birth_date,
    death_date,
    sex_code,
    race_code,
    esrd_indicator,
    state_code,
    county_code,

    part_a_coverage_months,
    part_b_coverage_months,
    hmo_coverage_months,
    part_d_coverage_months,

    has_alzheimer_or_dementia,
    has_chronic_heart_failure,
    has_chronic_kidney_disease,
    has_cancer,
    has_copd,
    has_depression,
    has_diabetes,
    has_ischemic_heart_disease,
    has_osteoporosis,
    has_rheumatoid_or_osteoarthritis,
    has_stroke_or_tia,

    medicare_reimbursement_inpatient,
    beneficiary_responsibility_inpatient,
    primary_payer_payment_inpatient,

    medicare_reimbursement_outpatient,
    beneficiary_responsibility_outpatient,
    primary_payer_payment_outpatient,

    medicare_reimbursement_carrier,
    beneficiary_responsibility_carrier,
    primary_payer_payment_carrier,

    source_year as latest_source_year,
    source_file_name,
    ingested_at

from ranked_beneficiaries
where beneficiary_year_rank = 1