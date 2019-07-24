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
import tools
import config as cfg

legacy_sockets  = [
                    energenie.Devices.ENER002(0),
                    energenie.Devices.ENER002(1),
                    energenie.Devices.ENER002(2),
                    energenie.Devices.ENER002(3),
                    energenie.Devices.ENER002(4),
                  ]

smooth = tools.Average() # Define the smoothed genaration average

def energy_monitor_loop():

    # Process any received messages from the real radio, time out after 30 s
    energenie.loop(cfg.receive_wait)
    GENORATION = 0
    # check all devices in the registry and report there battery power
    for d in energenie.registry.devices():
        try:
            if d.product_id == energenie.Devices.PRODUCTID_MIHO006:
                if d.get_apparent_power() > 50: # weed out the low genaration or power used to run meater
                    # work out the power factor for later
                    pf = ((d.get_current()/240)*d.get_apparent_power())
                    # working out the watts = amps x volts
                    GENORATION =(240*d.get_current())/(0.84) # device by power factor
                    # if less than 1 watt this can be 0 as may just be the power for the meater
                    # digital meaters can use up to 3wh
                else:
                    GENORATION = 0 # set no not genarating power

                smooth.add(GENORATION)

                # print data for device
                print("Generating: %.2fKw/h, Smoth Average %.2fKw/h, Battery: %.0f%%" % (GENORATION/1000, smooth.average()/1000, d.get_battery_life()))
        except Exception as e:
            print(e) # print exception

    supply = GENORATION - cfg.base_watts
    if cfg.use_smoothing:
        supply = smooth.average() - cfg.base_watts

    supply = round(supply)

    if supply > 0:
        for socket in cfg.legacy_sockets:
            if supply > socket['watts'] :
                supply -= socket['watts']
                legacy_sockets[socket['socket']].turn_on()
            else:
                legacy_sockets[socket['socket']].turn_off()
            time.sleep(1) # let sockets settle to reduce rf noise
        print("Remaining Supply %sw" % supply)
    else:
        legacy_sockets[0].turn_off()


def incoming(address, message):
    #print("Handeling incoming from %s" % str(address))
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
        legacy_sockets[0].turn_on()
    else:
        legacy_sockets[0].turn_off()

    # provide a default message handler
    energenie.fsk_router.when_incoming(incoming)
    print("Logging to file:%s" % Logger.LOG_FILENAME)

    try:
        while True:
            energy_monitor_loop()
    finally:
        energenie.finished()

# END
