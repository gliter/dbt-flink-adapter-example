#!/bin/bash

kafka-topics --delete --topic clickstream --bootstrap-server localhost:9092
kafka-topics --delete --topic balance-change --bootstrap-server localhost:9092
kafka-topics --delete --topic loan-change --bootstrap-server localhost:9092

kafka-topics --delete --topic high-loan --bootstrap-server localhost:9092

kafka-topics --bootstrap-server localhost:9092 --create --topic clickstream --partitions 1
kafka-topics --bootstrap-server localhost:9092 --create --topic balance-change --partitions 1
kafka-topics --bootstrap-server localhost:9092 --create --topic loan-change --partitions 1

kafka-topics --bootstrap-server localhost:9092 --create --topic high-loan --partitions 1
