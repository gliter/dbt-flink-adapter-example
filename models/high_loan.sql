select *
from {{ source('kafka', 'trx') }}
where source = 'credit'
and target = 'deposit'
and amount > 5000