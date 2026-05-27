with daily_bronze_counts as (
    select
        'inpatient' as claim_type,
        feed_date,
        count(*) as bronze_daily_rows
    from {{ source('bronze', 'daily_inpatient_claims') }}
    group by feed_date

    union all

    select
        'outpatient' as claim_type,
        feed_date,
        count(*) as bronze_daily_rows
    from {{ source('bronze', 'daily_outpatient_claims') }}
    group by feed_date
),

daily_silver_counts as (
    select
        claim_type,
        feed_date,
        count(*) as silver_daily_rows
    from {{ ref('silver_claims') }}
    where source_system = 'daily_synthetic'
    group by claim_type, feed_date
)

select
    b.feed_date,
    b.claim_type,
    b.bronze_daily_rows,
    coalesce(s.silver_daily_rows, 0) as silver_daily_rows,
    b.bronze_daily_rows - coalesce(s.silver_daily_rows, 0) as rejected_rows

from daily_bronze_counts b
left join daily_silver_counts s
    on b.claim_type = s.claim_type
   and b.feed_date = s.feed_date