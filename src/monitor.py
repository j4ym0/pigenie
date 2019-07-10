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
import config as cfg

legacy_all_sockets  = energenie.Devices.ENER002(0)
legacy_socket_1     = energenie.Devices.ENER002(1)
legacy_socket_2     = energenie.Devices.ENER002(2)
legacy_socket_3     = energenie.Devices.ENER002(3)
legacy_socket_4     = energenie.Devices.ENER002(4)

smooth = tools.Average() # Define the smoothed genaration average

def energy_monitor_loop():

    # Process any received messages from the real radio, time out after 30 s
    energenie.loop()

    # check all devices in the registry and report there battery power
    for d in energenie.registry.devices():
        try:
            if d.product_id == energenie.Devices.PRODUCTID_MIHO006:
                # work out the power factor for later
                pf = ((d.get_current()/240)*d.get_apparent_power())
                # working out the watts = amps x volts
                GENORATION = (240*d.get_current())/(0.84) # device by power factor
                # if less than 1 watt this can be 0 as may just be the power for the meater
                # digital meaters can use up to 3wh
                if GENORATION < 5:
                    GENORATION = 0
                # devide by 1000 to get KWh
                GENORATION = GENORATION/1000

                smooth.add(GENORATION)

                # give us a rugh estimate of battery power
                bat_percent = d.get_battery_life()

                # print data for device
                print("Generating: %.2fKw/h, Smoth Average %.2fKw/h, Battery: %.0f%%" % (GENORATION, smooth.average(), bat_percent))
        except:
            pass # Ignore

    if GENORATION > 0.5:
        legacy_socket_1.turn_on()
    else:
        legacy_socket_1.turn_off()


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

    # set default state of sockets
    if cfg.default_switch_state:
        legacy_all_sockets.turn_on()
    else:
        legacy_all_sockets.turn_off()

    # provide a default message handler
    energenie.fsk_router.when_incoming(incoming)
    print("Logging to file:%s" % Logger.LOG_FILENAME)

    try:
        while True:
            energy_monitor_loop()
    finally:
        energenie.finished()

# END
