import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton
from rx.subjects import Subject

class HelloWorld(QWidget):
    def __init__(self, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)
        self.events = Subject()
        self.resize(250, 150)
        self.move(350, 200)
        self.setWindowTitle('hello world')
        self.button = QPushButton('hello', self)
        self.button.clicked.connect(self.button_clicked)
        self._times_clicked = 0

    def button_clicked(self):
        self._times_clicked += 1
        self.events.on_next({
            'source': 'hello_world',
            'data': 'clicked',
            'count': self._times_clicked
        })

if __name__ == '__main__':
    app = QApplication(sys.argv)
    hello_world = HelloWorld()
    hello_world.show()
    hello_world.events \
        .buffer_with_time(500) \
        .filter(lambda x: len(x) > 0) \
        .map(lambda x: x[-1]) \
        .subscribe(lambda x: hello_world.setWindowTitle(
            '{} times clicked'.format(x['count'])))
    sys.exit(app.exec_())
