import platform
import time

import usb.core
import usb.util


class RocketError(Exception):
    pass


class Rocket(object):
    COMMANDS = {
        'DOWN': 0x01,
        'UP': 0x02,
        'LEFT': 0x04,
        'RIGHT': 0x08,
        'FIRE': 0x10,
        'STOP': 0x20,
    }

    MAX_ROTATION_DURATION = {
        'Thunder': 6,
        'Original': 15.75,
    }

    MAX_PITCH_DURATION = {
        'Thunder': 0.65,
        'Original': 3.05,
    }

    MAX_SHOTS = {
        'Thunder': 4,
        'Original': 3,
    }

    LED = {
        'Thunder': True,
        'Original': False,
    }

    def __init__(self, calibrate_x=None, calibrate_y=None):
        self.device = None
        self.device_type = None
        self.x = None
        self.y = None
        self.led_state = None

        # Allow the invoke to specify their own MAX_* values

        self.calibrate_x = calibrate_x
        self.calibrate_y = calibrate_y

        # Tested only with the Cheeky Dream Thunder
        # and original USB Launcher

        self.device = usb.core.find(idVendor=0x2123, idProduct=0x1010)

        if self.device is None:
            self.device = usb.core.find(idVendor=0x0a81, idProduct=0x0701)
            if self.device is None:
                raise RocketError('Missile device not found')
            else:
                self.device_type = 'Original'
        else:
            self.device_type = 'Thunder'

        # On Linux we need to detach usb HID first
        if platform.system() == 'Linux':
            try:
                self.device.detach_kernel_driver(0)
            except Exception as e:
                pass # already unregistered    

        self.device.set_configuration()

        if self.has_led:
            self.led(False)
        self.park()

    @property
    def max_rotation_duration(self):
        return self.calibrate_x or self.MAX_ROTATION_DURATION[self.device_type]

    @property
    def max_pitch_duration(self):
        return self.calibrate_y or self.MAX_PITCH_DURATION[self.device_type]

    @property
    def max_shots(self):
        return self.MAX_SHOTS[self.device_type]

    @property
    def has_led(self):
        return self.LED[self.device_type]

    def raw_command(self, cmd):
        if self.device_type == 'Thunder':
            self.device.ctrl_transfer(0x21, 0x09, 0, 0, [0x02, cmd, 0x00,0x00,0x00,0x00,0x00,0x00])
        elif self.device_type == 'Original':
            self.device.ctrl_transfer(0x21, 0x09, 0x0200, 0, [cmd])

    def led(self, status):
        if self.has_led:
            self.led_state = bool(status)
            self.device.ctrl_transfer(0x21, 0x09, 0, 0, [0x03, int(status), 0x00,0x00,0x00,0x00,0x00,0x00])
        else:
            raise RocketError('There is no LED on this device')

    def move(self, direction, duration):
        self.raw_command(self.COMMANDS[direction.upper()])
        time.sleep(duration)
        self.raw_command(self.COMMANDS['STOP'])

    def constrain_left(self, val):
        return max(0, min(val, self.x))

    def constrain_right(self, val):
        return max(0, min(val, 1.0 - self.x))

    def constrain_up(self, val):
        return max(0, min(val, 1.0 - self.y))

    def constrain_down(self, val):
        return max(0, min(val, self.y))

    def move_to(self, x, y):
        if x > self.x:
            self.move('RIGHT', self.max_rotation_duration * self.constrain_right(x - self.x))
        elif x < self.x:
            self.move('LEFT', self.max_rotation_duration * self.constrain_left(self.x - x))

        if y > self.y:
            self.move('UP', self.max_pitch_duration * self.constrain_up(y - self.y))
        elif y < self.y:
            self.move('DOWN', self.max_pitch_duration * self.constrain_down(self.y - y))

        self.x = min(1, max(0, x))
        self.y = min(1, max(0, y))

    def fire(self, count, led=True):
        if led:
            self.led(True)

        count = min(self.max_shots, max(1, count))
        time.sleep(0.5)
        for _ in range(count):
            self.raw_command(self.COMMANDS['FIRE'])
            time.sleep(4.5)

        if led:
            self.led(False)

    def park(self):
        self.move('DOWN', self.max_pitch_duration * 1.2)
        self.move('LEFT', self.max_rotation_duration * 1.2)
        self.x = 0
        self.y = 0
