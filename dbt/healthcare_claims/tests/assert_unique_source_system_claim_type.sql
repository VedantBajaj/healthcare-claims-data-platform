select
    source_system,
    claim_type,
    count(*) as row_count
from {{ ref('mart_claims_by_source_system') }}
group by source_system, claim_type
having count(*) > 1