select
    pipeline_name,
    run_id,
    feed_date,

    min(started_at) as started_at,
    max(ended_at) as ended_at,

    extract(
        epoch from max(ended_at) - min(started_at)
    )::numeric as duration_seconds,

    count(*) as files_processed,
    sum(rows_loaded) as total_rows_loaded,

    count(*) filter (
        where status = 'success'
    ) as successful_files,

    count(*) filter (
        where status = 'failed'
    ) as failed_files,

    case
        when count(*) filter (where status = 'failed') > 0
            then 'failed'
        else 'success'
    end as run_status

from {{ source('audit', 'pipeline_run_log') }}
group by
    pipeline_name,
    run_id,
    feed_date