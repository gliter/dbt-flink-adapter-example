import json
from dataclasses import dataclass
import time
from datetime import datetime
from random import randrange

from doge_datagen import Transition, SubjectFactory, DataOnlineGenerator, KafkaSinkFactory


@dataclass
class User:
    user_id: int
    deposit_balance: int = 0
    credit_balance: int = 0
    last_tx_source: str = None
    last_tx_target: str = None
    last_tx_amount: str = None

    def __hash__(self):
        return self.user_id


class UserFactory(SubjectFactory[User]):
    def __init__(self):
        super().__init__()
        self.current_id = 0

    def create(self) -> User:
        user = User(self.current_id)
        self.current_id += 1
        user.deposit_balance = randrange(0, 10000)
        user.credit_balance = randrange(-10000, 0)
        return user


def income_callback(subject: User, transition: Transition):
    income = randrange(500, 2000)
    subject.deposit_balance += income
    subject.last_tx_source = 'ext'
    subject.last_tx_target = 'deposit'
    subject.last_tx_amount = income
    return True


def payment_callback(subject: User, transition: Transition):
    payment = randrange(10, 1000)
    if payment > subject.deposit_balance:
        return False
    subject.deposit_balance -= payment
    subject.last_tx_source = 'deposit'
    subject.last_tx_target = 'ext'
    subject.last_tx_amount = payment
    return True


def take_loan_callback(subject: User, transition: Transition):
    loan = randrange(1000, 10000)
    subject.credit_balance -= loan
    subject.deposit_balance += loan
    subject.last_tx_source = 'credit'
    subject.last_tx_target = 'deposit'
    subject.last_tx_amount = loan
    return True


def pay_loan_callback(subject: User, transition: Transition):
    loan_payment = randrange(100, 1000)
    if loan_payment > -subject.credit_balance:
        loan_payment = -subject.credit_balance
    if loan_payment > subject.deposit_balance:
        return False
    subject.credit_balance += loan_payment
    subject.deposit_balance -= loan_payment
    subject.last_tx_source = 'deposit'
    subject.last_tx_target = 'credit'
    subject.last_tx_amount = loan_payment
    return True


def key_function(subject: User, transition: Transition) -> str:
    return str(subject.user_id)


def convert_timestamp(timestamp: int) -> str:
    return datetime.fromtimestamp(timestamp / 1000).strftime("%Y-%m-%dT%H:%M:%S.%f")


def clickstream_value_function(timestamp: int, subject: User, transition: Transition) -> str:
    value = {
        'event_timestamp': convert_timestamp(timestamp),
        'user_id': subject.user_id,
        'event': transition.trigger
    }
    return json.dumps(value)

def balance_value_function(timestamp: int, subject: User, transition: Transition) -> str:
    value = {
        'user_id': subject.user_id,
        'deposit_balance': subject.deposit_balance,
        'credit_balance': subject.credit_balance
    }
    return json.dumps(value)

def trx_value_function(timestamp: int, subject: User, transition: Transition) -> str:
    value = {
        'event_timestamp': convert_timestamp(timestamp),
        'user_id': subject.user_id,
        'source': subject.last_tx_source,
        'target': subject.last_tx_target,
        'amount': subject.last_tx_amount,
        'deposit_balance_after_trx': subject.deposit_balance,
        'credit_balance_after_trx': subject.credit_balance,
    }
    return json.dumps(value)


if __name__ == '__main__':
    factory = KafkaSinkFactory(['localhost:9092'], 'doge-kafka-example')
    balance_sink = factory.create('init-balance', key_function, balance_value_function)
    clickstream_sink = factory.create('clickstream', key_function, clickstream_value_function)
    trx_sink = factory.create('trx', key_function, trx_value_function)

    datagen = DataOnlineGenerator(['init', 'offline', 'online', 'loan_screen'], 'init', UserFactory(), 10, 60000, 10000, timestamp_start=round(time.time()*1000))
    datagen.add_transition('init', 'init', 'offline', 100, event_sinks=[balance_sink])
    datagen.add_transition('income', 'offline', 'offline', 0.01, action_callback=income_callback, event_sinks=[clickstream_sink, trx_sink])
    datagen.add_transition('payment', 'offline', 'offline', 0.2, action_callback=payment_callback, event_sinks=[clickstream_sink, trx_sink])
    datagen.add_transition('login', 'offline', 'online', 0.1, event_sinks=[clickstream_sink])
    datagen.add_transition('logout', 'online', 'offline', 65, event_sinks=[clickstream_sink])
    datagen.add_transition('open_loan_screen', 'online', 'loan_screen', 30, event_sinks=[clickstream_sink])
    datagen.add_transition('close_loan_screen', 'loan_screen', 'online', 40, event_sinks=[clickstream_sink])
    datagen.add_transition('take_loan', 'loan_screen', 'online', 10,
                           action_callback=take_loan_callback, event_sinks=[clickstream_sink, trx_sink])
    datagen.add_transition('pay_loan', 'online', 'online', 5,
                           action_callback=pay_loan_callback, event_sinks=[clickstream_sink, trx_sink])

    datagen.start()

