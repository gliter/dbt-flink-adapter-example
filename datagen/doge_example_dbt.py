import json
from dataclasses import dataclass
from random import randrange

from doge_datagen import Transition, SubjectFactory, DataOnlineGenerator, KafkaSinkFactory


@dataclass
class User:
    user_id: int
    balance: int
    loan_balance: int
    loan_balance_change: int
    balance_change: int

    def __hash__(self):
        return self.user_id


class UserFactory(SubjectFactory[User]):
    def __init__(self):
        super().__init__()
        self.current_id = 0

    def create(self) -> User:
        user = User(self.current_id, randrange(0, 1000), 0, 0, 0)
        self.current_id += 1
        return user


def income_callback(subject: User, transition: Transition):
    income = randrange(500, 2000)
    subject.balance += income
    subject.balance_change = income
    return True


def spending_callback(subject: User, transition: Transition):
    payment = randrange(10, 100)
    if payment > subject.balance:
        return False
    subject.balance -= payment
    subject.balance_change = -payment
    return True


def take_loan_callback(subject: User, transition: Transition):
    loan = randrange(1000, 10000)
    subject.loan_balance += loan
    subject.balance += loan
    subject.balance_change = loan
    subject.loan_balance_change = loan
    return True

def pay_loan_callback(subject: User, transition: Transition):
    loan_payment = randrange(100, 1000)
    if loan_payment > subject.balance or loan_payment > subject.loan_balance:
        return False
    subject.loan_balance -= loan_payment
    subject.balance -= loan_payment
    subject.balance_change = -loan_payment
    subject.loan_balance_change = -loan_payment
    return True

def create_generator(clickstream_sink, balance_change_sink, loan_balance_change_sink):
    datagen = DataOnlineGenerator(['offline', 'online', 'loan_screen'], 'offline', UserFactory(), 10, 60000, 10000)
    datagen.add_transition('income', 'offline', 'offline', 0.01, action_callback=income_callback, event_sinks=[clickstream_sink, balance_change_sink])
    datagen.add_transition('spending', 'offline', 'offline', 0.1, action_callback=spending_callback, event_sinks=[clickstream_sink, balance_change_sink])
    datagen.add_transition('login', 'offline', 'online', 0.1, event_sinks=[clickstream_sink])
    datagen.add_transition('logout', 'online', 'offline', 65, event_sinks=[clickstream_sink])
    datagen.add_transition('open_loan_screen', 'online', 'loan_screen', 30, event_sinks=[clickstream_sink])
    datagen.add_transition('close_loan_screen', 'loan_screen', 'online', 40, event_sinks=[clickstream_sink])
    datagen.add_transition('take_loan', 'loan_screen', 'online', 10,
                           action_callback=take_loan_callback, event_sinks=[clickstream_sink, balance_change_sink, loan_balance_change_sink])
    datagen.add_transition('pay_loan', 'online', 'online', 5,
                           action_callback=pay_loan_callback, event_sinks=[clickstream_sink, balance_change_sink, loan_balance_change_sink])
    return datagen

def key_function(subject: User, transition: Transition) -> str:
    return str(subject.user_id)

def clickstream_value_function(timestamp: int, subject: User, transition: Transition) -> str:
    value = {
        'timestamp': timestamp,
        'user_id': subject.user_id,
        'balance': subject.balance,
        'loan_balance': subject.loan_balance,
        'event': transition.trigger
    }
    return json.dumps(value)

def balance_change_value_function(timestamp: int, subject: User, transition: Transition) -> str:
    value = {
        'timestamp': timestamp,
        'user_id': subject.user_id,
        'balance_change': subject.balance_change,
        'event': transition.trigger
    }
    return json.dumps(value)

def loan_change_value_function(timestamp: int, subject: User, transition: Transition) -> str:
    value = {
        'timestamp': timestamp,
        'user_id': subject.user_id,
        'loan_balance_change': subject.loan_balance_change,
        'event': transition.trigger
    }
    return json.dumps(value)

if __name__ == '__main__':
    factory = KafkaSinkFactory(['localhost:9092'], 'doge-kafka-example')
    clickstream_sink = factory.create('clickstream', key_function, clickstream_value_function)
    balance_change_sink = factory.create('balance-change', key_function, balance_change_value_function)
    loan_change_sink = factory.create('loan-change', key_function, loan_change_value_function)

    datagen = create_generator(clickstream_sink, balance_change_sink, loan_change_sink)

    datagen.start()

