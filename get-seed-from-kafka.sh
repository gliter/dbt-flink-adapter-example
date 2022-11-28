#!/bin/bash

BOOTSTRAP_SERVER="localhost:9092"

get_seed_from_kafka() {
    topic=$1
    output_path=$2
    columns=$3

    echo $columns > $output_path
    kafka-console-consumer --bootstrap-server localhost:9092 --topic $topic --from-beginning --timeout-ms 5000 2>/dev/null | sed -r 's/\s*\"[A-Za-z\_]+\"+:\s*//g' | sed -r 's/[\{\}\"]//g' >> $output_path
}

get_seed_from_kafka "init-balance" "./seeds/init_balance.csv" "user_id,deposit_balance,credit_balance" &
get_seed_from_kafka "clickstream" "./seeds/clickstream.csv" "event_timestamp,user_id,event" &
get_seed_from_kafka "trx" "./seeds/trx.csv" "event_timestamp,user_id,source,target,amount,deposit_balance_after_trx,credit_balance_after_trx" &
wait < <(jobs -p)
