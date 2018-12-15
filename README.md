# pydream-rocket

Control Dream Cheeky USB rocket launchers.  See https://github.com/codedance/Retaliation for inspiration/source.

## Permission Denied error

To work around this:

    # You do not have to do this if you're already in the dialout group
    $ sudo usermod -a -G dialout $(whoami)
    # Log out and log back in
    $ sudo nano /etc/udev/rules.d/99-dreamcheeky-rocket.rules
    # Add the following lines:
    SUBSYSTEM=="usb", ATTRS{idVendor}=="2123", ATTRS{idProduct}=="1010", MODE="0666", GROUP="dialout"
    SUBSYSTEM=="usb", ATTRS{idVendor}=="0a81", ATTRS{idProduct}=="0701", MODE="0666", GROUP="dialout"
    # And then run
    $ sudo service udev restart