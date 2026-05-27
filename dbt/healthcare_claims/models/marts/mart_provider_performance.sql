select
    provider_id,
    claim_type,

    count(*) as total_claims,
    count(distinct beneficiary_id) as unique_beneficiaries,

    sum(claim_payment_amount) as total_claim_payment_amount,
    avg(claim_payment_amount) as average_claim_payment_amount,

    count(*) filter (
        where claim_start_date is null
    ) as claims_missing_start_date,

    count(*) filter (
        where claim_payment_amount < 0
    ) as negative_payment_claims

from {{ ref('silver_claims') }}
where provider_id is not null
group by provider_id, claim_type