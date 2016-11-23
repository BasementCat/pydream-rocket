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
    MAX_ROTATION_DURATION = 5.5
    MAX_PITCH_DURATION = 1.0

    def __init__(self):
        self.device = None
        self.device_type = None
        self.x = None
        self.y = None

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
            except Exception, e:
                pass # already unregistered    

        self.device.set_configuration()

        self.park()

    def raw_command(self, cmd):
        if self.device_type == 'Thunder':
            self.device.ctrl_transfer(0x21, 0x09, 0, 0, [0x02, cmd, 0x00,0x00,0x00,0x00,0x00,0x00])
        elif self.device_type == 'Original':
            self.device.ctrl_transfer(0x21, 0x09, 0x0200, 0, [cmd])

    def led(self, status):
        if self.device_type == 'Thunder':
            self.device.ctrl_transfer(0x21, 0x09, 0, 0, [0x03, int(status), 0x00,0x00,0x00,0x00,0x00,0x00])
        elif self.device_type == 'Original':
            raise RocketError('There is no LED on this device')

    def move(self, direction, duration):
        self.raw_command(self.COMMANDS[direction.upper()])
        time.sleep(duration)
        self.raw_command(self.COMMANDS['STOP'])

    def move_to(self, x, y):
        if x > self.x:
            self.move('RIGHT', self.MAX_ROTATION_DURATION * (x - self.x))
        elif x < self.x:
            self.move('LEFT', self.MAX_ROTATION_DURATION * (self.x - x))

        if y > self.y:
            self.move('UP', self.MAX_ROTATION_DURATION * (y - self.y))
        elif y < self.y:
            self.move('DOWN', self.MAX_ROTATION_DURATION * (self.y - y))

        self.x = x
        self.y = y

    def fire(self, count, led=True):
        if led:
            self.led(True)

        count = min(4, max(1, count))
        time.sleep(0.5)
        for _ in range(count):
            self.raw_command(self.COMMANDS['FIRE'])
            time.sleep(4.5)

        if led:
            self.led(False)

    def park(self):
        self.move('DOWN', self.MAX_PITCH_DURATION * 1.2)
        self.move('LEFT', self.MAX_ROTATION_DURATION * 1.2)
        self.x = 0
        self.y = 0
