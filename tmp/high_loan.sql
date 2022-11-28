select /** mode('streaming') */ *
from {{ source('kafka', 'trx') }}
/*where source = 'credit'
and target = 'deposit'
and credit_balance_after_trx < -10000
and deposit_balance_after_trx - amount < 5000*/