select
    claim_type,
    count(*) as total_claims,
    count(distinct beneficiary_id) as unique_beneficiaries,
    count(distinct provider_id) as unique_providers,

    count(*) filter (
        where claim_start_date is null
    ) as claims_missing_start_date,

    count(*) filter (
        where claim_payment_amount < 0
    ) as negative_payment_claims,

    min(claim_start_date) as earliest_claim_start_date,
    max(claim_start_date) as latest_claim_start_date

from {{ ref('silver_claims') }}
group by claim_type