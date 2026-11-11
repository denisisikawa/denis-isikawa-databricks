-- A returned row fails: all synthetic monthly costs and counts must be positive.
select *
from {{ ref('fct_monthly_costs') }}
where total_amount_brl <= 0
   or transaction_count <= 0
