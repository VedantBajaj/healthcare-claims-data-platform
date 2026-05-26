with inpatient_claims as (
    select
        beneficiary_id,
        claim_id,
        claim_segment,
        claim_type,

        claim_start_date,
        claim_end_date,
        admission_date,
        discharge_date,

        provider_id,

        claim_payment_amount,
        primary_payer_claim_paid_amount,
        pass_through_per_diem_amount,
        inpatient_deductible_amount,
        part_a_coinsurance_liability_amount,
        blood_deductible_liability_amount,
        utilization_day_count,

        null::numeric as part_b_deductible_amount,
        null::numeric as part_b_coinsurance_amount,

        attending_physician_npi,
        operating_physician_npi,
        other_physician_npi,

        admitting_diagnosis_code,
        primary_diagnosis_code,
        diagnosis_code_2,
        diagnosis_code_3,
        diagnosis_code_4,
        diagnosis_code_5,
        diagnosis_code_6,
        diagnosis_code_7,
        diagnosis_code_8,
        diagnosis_code_9,
        diagnosis_code_10,

        procedure_code_1,
        procedure_code_2,
        procedure_code_3,
        procedure_code_4,
        procedure_code_5,
        procedure_code_6,

        drg_code,

        hcpcs_code_1,
        hcpcs_code_2,
        hcpcs_code_3,
        hcpcs_code_4,
        hcpcs_code_5,

        source_file_name,
        ingested_at

    from {{ ref('stg_inpatient_claims') }}
),

outpatient_claims as (
    select
        beneficiary_id,
        claim_id,
        claim_segment,
        claim_type,

        claim_start_date,
        claim_end_date,
        null::date as admission_date,
        null::date as discharge_date,

        provider_id,

        claim_payment_amount,
        primary_payer_claim_paid_amount,
        null::numeric as pass_through_per_diem_amount,
        null::numeric as inpatient_deductible_amount,
        null::numeric as part_a_coinsurance_liability_amount,
        blood_deductible_liability_amount,
        null::numeric as utilization_day_count,

        part_b_deductible_amount,
        part_b_coinsurance_amount,

        attending_physician_npi,
        operating_physician_npi,
        other_physician_npi,

        admitting_diagnosis_code,
        primary_diagnosis_code,
        diagnosis_code_2,
        diagnosis_code_3,
        diagnosis_code_4,
        diagnosis_code_5,
        diagnosis_code_6,
        diagnosis_code_7,
        diagnosis_code_8,
        diagnosis_code_9,
        diagnosis_code_10,

        procedure_code_1,
        procedure_code_2,
        procedure_code_3,
        procedure_code_4,
        procedure_code_5,
        procedure_code_6,

        null::text as drg_code,

        hcpcs_code_1,
        hcpcs_code_2,
        hcpcs_code_3,
        hcpcs_code_4,
        hcpcs_code_5,

        source_file_name,
        ingested_at

    from {{ ref('stg_outpatient_claims') }}
),

unioned_claims as (
    select * from inpatient_claims
    union all
    select * from outpatient_claims
)

select
    {{ dbt_utils.generate_surrogate_key([
        'claim_id',
        'claim_segment',
        'claim_type',
        'beneficiary_id'
    ]) }} as claim_sk,

    *

from unioned_claims