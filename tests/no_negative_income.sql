select /** fetch_timeout_ms(5000) mode('streaming') */
  *
from {{ ref('joined_data')}}
where
  event = 'income'
  and amount < 0