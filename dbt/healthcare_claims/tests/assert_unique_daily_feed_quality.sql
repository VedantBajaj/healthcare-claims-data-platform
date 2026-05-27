select
    feed_date,
    claim_type,
    count(*) as row_count
from {{ ref('mart_daily_claim_feed_quality') }}
group by feed_date, claim_type
having count(*) > 1