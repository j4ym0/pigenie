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

import api

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

    # check all devices in the registry and report there battery power
    for d in energenie.registry.devices():
        try:
            if d.capabilities.send:
                # work out the power factor for later
                pf = ((d.get_current()/230)*d.get_apparent_power())
                # working out the watts = amps x volts
                GENORATION = (230*d.get_current())
                # if less than 1 watt this can be 0 as may just be the power for the meter
                if GENORATION < 1:
                    GENORATION = 0
                # devide by 1000 to get KWh
                GENORATION = GENORATION/1000

                print("Generating: %.2fKw/h" % (pf, GENORATION))
                #
                print("Battery Power: %f" % d.get_battery_voltage())
        except:
            pass # Ignore

    time.sleep(APP_DELAY)

def incoming(address, message):
    print("Handeling incoming from %s" % str(address))
    try:
        c = energenie.Devices.DeviceFactory.get_device_from_id(address[1], address[2])
        c.handle_message(message)
        if c.product_id == energenie.Devices.PRODUCTID_MIHO006:
            api.report_to_api(c)
    except:
        pass # Ignore carnt find device

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
