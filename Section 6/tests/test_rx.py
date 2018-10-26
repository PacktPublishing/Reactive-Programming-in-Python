import unittest

from rx.testing import TestScheduler, ReactiveTest
from rx import Observable
from rx.subjects import Subject

class TestRx(unittest.TestCase):
    def test_interval(self):
        scheduler = TestScheduler()
        interval_time = 300
        def create():
            return Observable.interval(interval_time, scheduler)
        subscribed = 300
        disposed = 1400
        results = scheduler.start(create, created=1, subscribed=subscribed, disposed=disposed)
        print(results.messages)
        assert results.messages == [
            ReactiveTest.on_next(600, 0),
            ReactiveTest.on_next(900, 1),
            ReactiveTest.on_next(1200, 2),
        ]

    def test_custom_subject(self):
        scheduler = TestScheduler()
        self.mouse_click_stream = None
        self.click_count = 0
        def create(scheduler, state):
            self.mouse_click_stream = Subject()
        def click(scheduler, state):
            self.mouse_click_stream.on_next('clicked')
        def subscribe(scheduler, state):
            def update(i):
                self.click_count += 1
            self.mouse_click_stream.subscribe(update)
        scheduler.schedule_absolute(1, create)
        scheduler.schedule_absolute(2, click)
        scheduler.schedule_absolute(3, subscribe)
        scheduler.schedule_absolute(4, click)
        scheduler.schedule_absolute(5, click)
        results = scheduler.start()
        print(results.messages)
        assert self.click_count == 2

if __name__ == '__main__':
    unittest.main()
