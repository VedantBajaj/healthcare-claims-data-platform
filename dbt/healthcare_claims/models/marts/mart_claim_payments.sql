select
    claim_type,

    count(*) as total_claims,

    sum(claim_payment_amount) as total_claim_payment_amount,
    avg(claim_payment_amount) as average_claim_payment_amount,
    min(claim_payment_amount) as minimum_claim_payment_amount,
    max(claim_payment_amount) as maximum_claim_payment_amount,

    sum(primary_payer_claim_paid_amount) as total_primary_payer_paid_amount,

    sum(
        coalesce(claim_payment_amount, 0)
        + coalesce(primary_payer_claim_paid_amount, 0)
    ) as total_combined_paid_amount

from {{ ref('silver_claims') }}
group by claim_type