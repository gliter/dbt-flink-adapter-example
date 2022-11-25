select /** fetch_timeout_ms(5000) fetch_mode('streaming') */
  *
from {{ source("kafka", "balance_change")}}
where
  event = 'income'
  and balance_change < 0