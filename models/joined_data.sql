select cs.event_timestamp, cs.user_id, cs.event, trx.source, trx.target, trx.amount, trx.deposit_balance_after_trx, trx.credit_balance_after_trx
from {{ source('kafka', 'clickstream') }} as cs
join {{ source('kafka', 'trx') }} as trx
on cs.user_id = trx.user_id
and cs.event_timestamp = trx.event_timestamp