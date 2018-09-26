from rx import Observable
from rx.testing import TestScheduler

def print_value(x):
    print(x)
# Map

# In the last video, we loaded rows from a CSV file. We used the map
# operator on the observable. Now we're going to take a look at a few
# more examples of using map.

# The map operator will map a value into another value. You can use it
# to transform an object into something else.

# Here's how we subtract one from every number emitted by an
# Observable.
Observable.from_([1,2,3]).map(lambda x: x - 1).subscribe(print_value)

# When we run this code we see that 1 has become 0, 2 is now 1 and 3 is 2.

# Sometimes for dictionary and hash tables, we may want to add more
# data. This is how we would do so:
Observable.from_([{'a': 1}, {'b': 2}, {'c': 3}]).map(lambda data: {**data, 'hello': 'world'}).subscribe(print_value)

# TODO: FlatMap

# Next we have the flat map operator. This operator similar to map,
# except it will work across multiple observables that are emitting
# their own observables.

# Let's try a simple example.

# First we define a function that will return an Observable. It will
# read all lines and then create an Observable of just the last line
# of the file.
def read_last_line_from_file(filename):
    with open(filename) as file:
        lines = file.readlines()
        last_line = lines[-1]
        return Observable.just(last_line)

# Next we want to be able to read the data from the file test.csv and
# then in sequential order read the next file. The flat map will
# accept the last line of the file as a parameter. The final subscribe
# will have the data from the inner observable.
read_last_line_from_file('test.csv').flat_map(lambda line: read_last_line_from_file('test2.csv')).subscribe(print_value)
# The idea with flat map is to make it easy to use the first, outer
# observable, with the next, inner observable. This helps us avoid a
# pyramid of subscriptions.

# Window is similar to buffer, except it emits a nested observable
# rather than a list.

# For example, we want to take a range of numbers and in windows of 2
# items at a time.
print('window_with_count')
Observable.from_(range(3)).window_with_count(2).subscribe(print_value)
# You can see that if we use subscribe, the window will emit multiple
# observables. To convert each observable to a one value of each list,
# we can use flat_map.
print('window_with_count.flat_map')
Observable.from_(range(3)).window_with_count(2).flat_map(lambda x: x).subscribe(print_value)
# You can also use window_with_time to create windows of items based
# on intervals of milliseconds. Here we're going to create windows
# every 50 milliseconds and then for each observable emitted, we're
# going to count the number of items.
print('window_with_time')
test_scheduler = TestScheduler()
Observable.interval(50, test_scheduler).take_until(Observable.timer(100)).window_with_time(10).subscribe(lambda observable: observable.count().subscribe(print_value))
test_scheduler.start()
# If you run this code a few times, you'll see that we get a different number of items in each window.

# CombineLatest will emit items whenever any observable has an item to
# emit. This is a good way of combining items from multiple
# observables and streams of data into one stream.

# For example, we may want to have two sources of data open, one that
# reads files and another that receives data from a web server. With
# combine_latest we can combine the items from each of those sources
# and process them however we like with the other operators.

# Here's a small example of using combine latest.
print('-- Combine Latest')
test_scheduler = TestScheduler()
Observable.combine_latest(
    Observable.interval(1, test_scheduler).map(lambda x: 'a: {}'.format(x)),
    Observable.interval(2, test_scheduler).map(lambda x: 'b: {}'.format(x)),
    lambda a, b: '{}; {}'.format(a, b)
).take_until(Observable.timer(5)).subscribe(print_value)
test_scheduler.start()
# You can see that as it progresses, the current value of the A or B
# stream will be passed along with the updated value of the other
# stream. So in some cases we see the same number for A while the B
# number has increased, and vice versa. This is great when you want to
# combine items no matter which stream is emitting those items.

# Zip will emit items only when all observables have an item to
# emit. This is also another good way to combine streams of data and
# it's great because it can effectively block until all observables
# have items.

# For example, we could be opening files in multiple threads or
# subprocesses but we only want to process the information when all
# files have been

# Here's a small example of using zip.
print('-- Zip')
test_scheduler = TestScheduler()
Observable.zip(
    Observable.interval(1, test_scheduler).map(lambda x: 'a: {}'.format(x)),
    Observable.interval(2, test_scheduler).map(lambda x: 'b: {}'.format(x)),
    lambda a, b: '{}; {}'.format(a, b)
).take_until(Observable.timer(5)).subscribe(print_value)
test_scheduler.start()
# You can see that the numbers aren't printed until both items are
# emitted from the A and B stream.
