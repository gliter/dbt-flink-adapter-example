#!/bin/bash

kafka-topics --delete --topic clickstream --bootstrap-server localhost:9092 &
kafka-topics --delete --topic init-balance --bootstrap-server localhost:9092 &
kafka-topics --delete --topic trx --bootstrap-server localhost:9092 &

kafka-topics --delete --topic high-loan --bootstrap-server localhost:9092 &

wait < <(jobs -p)

kafka-topics --bootstrap-server localhost:9092 --create --topic clickstream --partitions 1 --config retention.ms=-1 &
kafka-topics --bootstrap-server localhost:9092 --create --topic init-balance --partitions 1 --config retention.ms=-1 &
kafka-topics --bootstrap-server localhost:9092 --create --topic trx --partitions 1 --config retention.ms=-1 &

kafka-topics --bootstrap-server localhost:9092 --create --topic high-loan --partitions 1 --config retention.ms=-1 &

wait < <(jobs -p)
