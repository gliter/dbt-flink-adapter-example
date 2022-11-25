select /** fetch_mode('streaming') */ *
from {{ source('kafka', 'loan_change') }}
where event = 'take_loan'
and loan_balance_change > 5000