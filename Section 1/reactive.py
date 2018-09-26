from rx import Observable

def print_number(x):
    print('The number is {}'.format(x))

Observable.from_(range(10)).subscribe(print_number)
