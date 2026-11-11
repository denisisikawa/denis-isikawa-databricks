-- Synthetic finance costs, normalized at transaction grain.
select
    cast(record_id as integer) as record_id,
    cast(month as date) as month,
    trim(cost_center) as cost_center,
    trim(category) as category,
    cast(amount_brl as decimal(18, 2)) as amount_brl,
    trim(source_system) as source_system
from {{ ref('finance_costs') }}
