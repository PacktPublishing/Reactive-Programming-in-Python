from rx import Observable

def print_value(value):
    print('{} is the value.'.format(value))

# From
Observable.from_(['abc', 'def', 'ghi']).subscribe(print_value)

def say_hello(name, callback):
    callback('hello {}!'.format(name))

# You can use from_callback to produce more observables using a
# function as a factory.
hello = Observable.from_callback(say_hello)
hello('Rudolf').subscribe(print_value)
hello('observable').subscribe(print_value)

# You can turn a list into an observable.
Observable.from_list([1, 2, 3]).subscribe(print_value)

# You can turn a list of arguments into an observable.
Observable.of(1, 2, 3, 'A', 'B', 'C').subscribe(print_value)

# And for testing, you can use "marbles". Marbles are a visual
# representation of when items are emitted through an observable.

# We have to import the marbles module to activate this function and
# we have to import the TestScheduler.
from rx.testing import marbles, TestScheduler

from rx.concurrency import timeout_scheduler, new_thread_scheduler

test_scheduler = TestScheduler()

# When you create an observable, you have the option of passing in a
# scheduler. The scheduler can be the Python Async IO scheduler, the
# scheduler from Tornado or the scheduler from Q.  The scheduler
# coordinates and executes events.
#
# In this case we use the test scheduler because it lets us control
# when events are executed.
Observable.from_marbles('--(a1)-(b2)---(c3)|', test_scheduler).subscribe(print_value)
# To execute the events in the observable with the test scheduler, we
# have to call the start method.
test_scheduler.start()

# Interval

# Intervals are great for continuously emitting items at a set time,
# for example every second, or every hour.

# As an example, we'll print out hello every 100 milliseconds until 1
# second has passed.
test_scheduler = TestScheduler()
Observable.interval(10, test_scheduler).take_until(Observable.timer(30)).subscribe(print_value)
test_scheduler.start()

# Buffer
print('-- Buffer')
# A buffer created from an observable will fill up with a certain
# number of items. It will only emit this set of buffered items when
# another observable emits an item.

# We're going to emit 2000 numbers and then buffer them every
# millisecond and print out the number of items in the buffer.
Observable.from_(range(2000)).buffer(Observable.interval(1)).subscribe(lambda buffer: print('# of items in buffer: {}'.format(len(buffer))))
print('-- Buffer with count')
Observable.from_(range(10)).buffer_with_count(3).subscribe(print_value)
print('-- Buffer with time')
test_scheduler = TestScheduler()
Observable.interval(10, test_scheduler).take_until(Observable.timer(30)).buffer_with_time(20).subscribe(print_value)
test_scheduler.start()

# Group By
print('-- Group By')
def key_selector(x):
    if x % 2 == 0:
        return 'even'
    return 'odd'

def subscribe_group_observable(group_observable):
    def print_count(count):
        print('Group Observable key "{}" contains {} items'.format(group_observable.key, count))
    group_observable.count().subscribe(print_count)

# In the list of 10 items, the group will be divided into two; evens
# and odds. Each group will have its own key.
groups = Observable.from_(range(3)).group_by(key_selector)
groups.subscribe(subscribe_group_observable)

# Sample
print('-- Sample')
test_scheduler = TestScheduler()
Observable.interval(1, test_scheduler).take_until(Observable.timer(30)).sample(3).subscribe(print_value)
test_scheduler.start()

# Max is an aggregate operator and gets the maximum value. This is
# useful when combined with buffer and sample and other operators
# because you can get the maximum value within a set of items, or
# within a few minutes or few hours.
print('-- Max')
Observable.from_([1,2,3,4,12,3,3,-10]).max(lambda x, y: x - y).subscribe(print_value)
