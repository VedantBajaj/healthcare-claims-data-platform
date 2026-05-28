select
    pipeline_name,
    run_id,
    feed_date,
    count(*) as row_count
from {{ ref('mart_pipeline_run_audit') }}
group by
    pipeline_name,
    run_id,
    feed_date
having count(*) > 1