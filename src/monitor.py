# mihome_energy_monitor.py  28/05/2016  D.J.Whale
#
# A simple demo of monitoring and logging energy usage of mihome devices
#
# Logs all messages to screen and to a file energenie.csv
# Any device that has a switch, it toggles it every 2 seconds.
# Any device that offers a power reading, it displays it.

import energenie
import Logger
import time

APP_DELAY    = 2
switch_state = False

def energy_monitor_loop():
    global switch_state

    # Process any received messages from the real radio
    energenie.loop()

    # For all devices in the registry, if they have a switch, toggle it
    for d in energenie.registry.devices():
        if d.has_switch():
            d.set_switch(switch_state)
    switch_state = not switch_state

    # For all devices in the registry and report there battery power
    for d in energenie.registry.devices():
        try:
            if d.capabilities.send == True:
                print(d)
                p = d.battery_voltage()
                print("Battery Power for %s: %2.f" % (d, p))
        except:
            pass # Ignore it if can't provide a power

    time.sleep(APP_DELAY)

def incoming(address, message):
    print("Handeling incoming from %s" % str(address))
    c = energenie.Devices.DeviceFactory.get_device_from_id(address[1], address[2])
    c.handle_message(message)
    Logger.logMessage(message)

if __name__ == "__main__":

    print("Starting energy monitor")

    energenie.init()
    energenie.discovery_auto()

    # provide a default message handler
    energenie.fsk_router.when_incoming(incoming)
    print("Logging to file:%s" % Logger.LOG_FILENAME)

    try:
        while True:
            energy_monitor_loop()
    finally:
        energenie.finished()

# END
