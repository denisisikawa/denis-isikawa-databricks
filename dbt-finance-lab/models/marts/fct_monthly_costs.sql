-- One row per reporting month, cost center, and category.
with base as (
    select * from {{ ref('stg_finance_costs') }}
)
select
    cast(month as varchar) || '|' || cost_center || '|' || category as cost_key,
    month,
    cost_center,
    category,
    cast(sum(amount_brl) as decimal(18, 2)) as total_amount_brl,
    count(*) as transaction_count
from base
group by month, cost_center, category
