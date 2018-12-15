import textwrap

import bottle

from . import Rocket


class HTTPServer(object):
    def __init__(self):
        self.rocket = Rocket()
        self.app = bottle.Bottle()

        self.app.get('/')(self.index)
        self.app.post('/move_to')(self.move_to)
        self.app.post('/led')(self.led)
        self.app.post('/fire')(self.fire)
        self.app.get('/state')(self.state)

    def _get_state(self):
        return {
            'led': self.rocket.led_state,
            'position': [self.rocket.x, self.rocket.y],
            'max_shots': self.rocket.max_shots
        }

    def index(self):
        return textwrap.dedent('''\
            <!DOCTYPE html>
            <html>
                <head>
                    <title>Rocket</title>
                    <style>
                        table {
                            float: left;
                        }
                    </style>
                </head>
                <body>
                    <table>
                        <tr><th colspan="3">Controls</th></td>
                        <tr>
                            <td>&nbsp;</td>
                            <td><button id="up">Up</button></td>
                            <td>&nbsp;</td>
                        </tr>
                        <tr>
                            <td><button id="left">Left</button></td>
                            <td><button id="fire">Fire</button></td>
                            <td><button id="right">Right</button></td>
                        </tr>
                        <tr>
                            <td>&nbsp;</td>
                            <td><button id="down">Down</button></td>
                            <td>&nbsp;</td>
                        </tr>
                    </table>
                    <table>
                        <tr><th colspan="1">LED</th></tr>
                        <tr><td><button id="led-on">On</button</td></tr>
                        <tr><td><button id="led-off">Off</button</td></tr>
                    </table>
                    <table>
                        <tr><th colspan="2">Move To</th></tr>
                        <tr>
                            <td><input type="text" name="x" id="move-x" /></td>
                            <td><input type="text" name="y" id="move-y" /></td>
                        </tr>
                        <tr>
                            <td colspan="2">
                                <input type="submit" value="Move" id="move" />
                            </td>
                        </tr>
                    </table>
                    <table>
                        <tr><td colspan="2">State</td></tr>
                        <tr><th>X Pos</th><td id="state-x-pos"></td></tr>
                        <tr><th>Y Pos</th><td id="state-y-pos"></td></tr>
                        <tr><th>LED</th><td id="state-led"></td></tr>
                        <tr><th>Max Shots</th><td id="state-max-shots"></td></tr>
                    </table>

                    <script>
                        (function() {
                            var state = null;
                            var btn = {
                                up: document.getElementById('up'),
                                down: document.getElementById('down'),
                                left: document.getElementById('left'),
                                right: document.getElementById('right'),
                                fire: document.getElementById('fire'),
                                led_on: document.getElementById('led-on'),
                                led_off: document.getElementById('led-off'),
                                move: document.getElementById('move'),
                            };
                            var data = {
                                move_x: document.getElementById('move-x'),
                                move_y: document.getElementById('move-y'),
                            };

                            var update_state = function() {
                                state = JSON.parse(this.responseText).state;
                                document.getElementById('state-x-pos').innerText = state.position[0];
                                document.getElementById('state-y-pos').innerText = state.position[1];
                                document.getElementById('state-led').innerText = state.led === null ? 'No LED' : (state.led ? 'On' : 'Off');
                                document.getElementById('state-max-shots').innerText = state.max_shots;
                            };

                            var get_state = function() {
                                var req = new XMLHttpRequest;
                                req.overrideMimeType("application/json");
                                req.open('GET', '/state', true);
                                req.onload  = update_state.bind(req);
                                req.send(null);
                            };

                            var change_led = function(val) {
                                var form = new FormData();
                                form.append("state", val.toString());

                                var req = new XMLHttpRequest;
                                req.overrideMimeType("application/json");
                                req.open('POST', '/led', true);
                                req.onload  = update_state.bind(req);
                                req.send(form);
                            };

                            var move_to = function(x, y) {
                                var form = new FormData();
                                form.append("x", x.toString());
                                form.append("y", y.toString());

                                var req = new XMLHttpRequest;
                                req.overrideMimeType("application/json");
                                req.open('POST', '/move_to', true);
                                req.onload  = update_state.bind(req);
                                req.send(form);
                            };

                            var fire = function() {
                                var form = new FormData();
                                form.append("count", 1);

                                var req = new XMLHttpRequest;
                                req.overrideMimeType("application/json");
                                req.open('POST', '/fire', true);
                                req.onload  = update_state.bind(req);
                                req.send(form);
                            };

                            btn.led_on.onclick = change_led.bind(window, 1);
                            btn.led_off.onclick = change_led.bind(window, 0);
                            btn.move.onclick = function() {
                                move_to(
                                    data.move_x.value,
                                    data.move_y.value,
                                );
                            };
                            btn.up.onclick = function() { move_to(state.position[0], Math.min(1, state.position[1] + 0.1)); };
                            btn.down.onclick = function() { move_to(state.position[0], Math.max(0, state.position[1] - 0.1)); };
                            btn.left.onclick = function() { move_to(Math.max(0, state.position[0] - 0.05), state.position[1]); };
                            btn.right.onclick = function() { move_to(Math.min(1, state.position[0] + 0.05), state.position[1]); };
                            btn.fire.onclick = fire

                            window.setInterval(get_state, 2000);
                            get_state();
                        })();
                    </script>
                </body>
            </html>
        ''')

    def move_to(self):
        try:
            self.rocket.move_to(float(bottle.request.forms.get('x') or 0), float(bottle.request.forms.get('y') or 0))
        except Exception as e:
            return {
                'result': False,
                'error': {
                    'type': e.__class__.__name__,
                    'message': str(e),
                },
                'state': self._get_state(),
            }
        else:
            return {
                'result': True,
                'state': self._get_state(),
            }

    def led(self):
        try:
            self.rocket.led(int(bottle.request.forms.get('state') or 0))
        except Exception as e:
            return {
                'result': False,
                'error': {
                    'type': e.__class__.__name__,
                    'message': str(e),
                },
                'state': self._get_state(),
            }
        else:
            return {
                'result': True,
                'state': self._get_state(),
            }

    def fire(self):
        try:
            self.rocket.fire(int(bottle.request.forms.get('count') or 0))
        except Exception as e:
            return {
                'result': False,
                'error': {
                    'type': e.__class__.__name__,
                    'message': str(e),
                },
                'state': self._get_state(),
            }
        else:
            return {
                'result': True,
                'state': self._get_state(),
            }

    def state(self):
        return {
            'result': True,
            'state': self._get_state(),
        }
