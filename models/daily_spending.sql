select window_start, window_end, user_id, sum(amount) as daily_spending
from table(
    tumble(table {{ ref('joined_data') }}, descriptor(event_timestamp), interval '1' days)
    )
where event = 'payment'
group by window_start, window_end, user_id