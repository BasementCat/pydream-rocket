import bottle

from . import Rocket


class HTTPServer(object):
    def __init__(self):
        self.rocket = Rocket()
        self.app = bottle.Bottle()

        self.app.post('/move_to')(self.move_to)
        self.app.post('/led')(self.led)
        self.app.post('/fire')(self.fire)
        self.app.get('/position')(self.position)

    def move_to(self):
        self.rocket.move_to(float(bottle.request.forms.get('x') or 0), float(bottle.request.forms.get('y') or 0))
        return {'result': True}

    def led(self):
        self.rocket.led(int(bottle.request.forms.get('state') or 0))
        return {'result': True}

    def fire(self):
        self.rocket.fire(int(bottle.request.forms.get('count') or 0))
        return {'result': True}

    def position(self):
        return {'result': {'x': self.rocket.x, 'y': self.rocket.y}}
