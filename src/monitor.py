# mihome_energy_monitor.py  28/05/2016  D.J.Whale
#
# A simple demo of monitoring and logging energy usage of mihome devices
#
# Logs all messages to screen and to a file energenie.csv
# Any device that has a switch, it toggles it every 2 seconds.
# Any device that offers a power reading, it displays it.

import energenie
import logger
import time
from datetime import datetime
import api
import tools
import config as cfg
import display
import importlib

legacy_sockets  = [
                    energenie.Devices.ENER002(0), # all OOK sockets
                    energenie.Devices.ENER002(1), # OOK socket programed as No. 1
                    energenie.Devices.ENER002(2), # OOK socket programed as No. 2
                    energenie.Devices.ENER002(3), # OOK socket programed as No. 3
                    energenie.Devices.ENER002(4), # OOK socket programed as No. 4
                  ]

smooth = tools.Average() # Define the smoothed genaration average
display = display.Display() # define the display so we can keep it updated


def energy_monitor_loop():

    # daily reset function
    if not cfg.last_reset_day == datetime.now().day:
        cfg.last_reset_day = datetime.now().day
        importlib.reload(cfg) # reload the config file every day
        for socket in cfg.legacy_sockets: # reset all the time counters for each legacy socket
            socket['elapsed_time'] = 0

    # Process any received messages from the real radio, time out after 30 s
    if not energenie.loop(cfg.receive_wait):
        logger.info("Timeout, nothing received")
        cfg.TIMEOUT_IRRITATION += 1
        logger.debug("Timeout irritation %i" % (cfg.TIMEOUT_IRRITATION))
        if not cfg.app_all_off and cfg.TIMEOUT_IRRITATION > 5:
            logger.info("Nothing received for a while. Turning all off")
            legacy_sockets[0].turn_off()
            cfg.app_all_off = True
        return False
    else:
        cfg.TIMEOUT_IRRITATION = 0

    display.emons_update(energenie.registry.devices())
    GENORATION = 0
    # check all devices in the registry and report there battery power
    for d in energenie.registry.devices():
        try:
            if d.product_id == energenie.Devices.PRODUCTID_MIHO006:
                if d.get_apparent_power() > 50: # weed out the low genaration or power used to run meater
                    # work out the power factor for later
                    pf = ((d.get_current()/240)*d.get_apparent_power())
                    # working out the watts = amps x volts
                    GENORATION = (240*d.get_current())/(0.84) # device by power factor
                    # if less than 1 watt this can be 0 as may just be the power for the meater
                    # digital meaters can use up to 3wh
                else:
                    GENORATION = 0 # set no not genarating power

                smooth.add(GENORATION)

                # print data for device
                logger.info("Generating: %.2fKw/h, Smoth Average %.2fKw/h, Battery: %.0f%%" % (GENORATION/1000, smooth.average()/1000, d.get_battery_life()))
        except Exception as e:
            logger.warning(e) # print exception

    if cfg.use_smoothing: GENORATION = smooth.average()
    supply = round(GENORATION - cfg.base_watts)

    if supply > 0:
        for socket in cfg.legacy_sockets:
            if socket['max_time'] > 0:
                if 'elapsed_time' not in socket:
                    socket['elapsed_time'] = 0
                    logger.verbose("zeroing")
                if 'current_timing' not in socket:
                    socket['current_timing'] = None

            if supply > socket['watts']:
                onoff = True
                if socket['max_time'] > 0:
                    if socket['elapsed_time'] >= socket['max_time']:
                        onoff = False
                    elif socket['current_timing'] is None:
                        socket['current_timing'] = time.time()
                    else:
                        if socket['max_time'] < (socket['elapsed_time']+(time.time()-socket['current_timing'])):
                            socket['elapsed_time'] = socket['elapsed_time']+time.time()-socket['current_timing']
                            logger.debug("socket %i above max_time" % socket['socket'])
                            onoff = False
                            socket['current_timing'] = None

                if onoff:
                    supply -= socket['watts']
                    legacy_sockets[socket['socket']].turn_on()
                    logger.debug("socket %i on" % socket['socket'])
                else:
                    legacy_sockets[socket['socket']].turn_off()
                    logger.debug("socket %i off" % socket['socket'])

            else:
                if socket['max_time'] > 0 and socket['current_timing'] is not None:
                    socket['elapsed_time'] = socket['elapsed_time']+time.time()-socket['current_timing']
                    logger.debug("elapsed_time")
                    socket['current_timing'] = None

                legacy_sockets[socket['socket']].turn_off()
                logger.debug("socket %i off" % socket['socket'])

            if socket['max_time'] > 0 and 'elapsed_time' in socket and socket['current_timing'] is not None:
                logger.info("Total Elapsed: %i and current elapsed: %i" % (socket['elapsed_time'], ((socket['elapsed_time']+(time.time()-socket['current_timing'])))))
            elif socket['max_time'] > 0 and 'elapsed_time' in socket:
                logger.debug("Total elapsed time: %i" % (socket['elapsed_time']))
            time.sleep(1) # let sockets settle to reduce rf noise
        logger.debug("Remaining Supply %sw" % supply)
        cfg.app_all_off = False
    else:
        if not cfg.app_all_off:
            legacy_sockets[0].turn_off()
            cfg.app_all_off = True

    display.usage_update(GENORATION, (GENORATION-supply))
    display.sockets_update(legacy_sockets, cfg.legacy_sockets)
    display.render(cfg.log_level)

def incoming(address, message):
    #print("Handeling incoming from %s" % str(address))
    try:
        c = energenie.Devices.DeviceFactory.get_device_from_id(address[1], address[2])
        c.handle_message(message)
        if c.product_id == energenie.Devices.PRODUCTID_MIHO006:
            api.report_to_api(c)
    except:
        pass # Ignore carnt find device

    logger.logMessage(message)

if __name__ == "__main__":

    # init global vars
    cfg.last_reset_day = datetime.now().day
    cfg.TIMEOUT_IRRITATION = 0

    logger.info("Starting energy monitor")

    energenie.init()
    energenie.discovery_auto()

    # set default state of sockets
    if cfg.default_switch_state:
        legacy_sockets[0].turn_on()
        cfg.app_all_off = False
    else:
        legacy_sockets[0].turn_off()
        cfg.app_all_off = True

    # provide a default message handler
    energenie.fsk_router.when_incoming(incoming)
    logger.debug("Debug Logging to file:%s" % cfg.LOG_FILENAME)
    logger.debug("Data Logging File:%s" % cfg.CSV_FILENAME)

    try:
        while True:
            energy_monitor_loop()
    except KeyboardInterrupt:
        print("Bye!")
    finally:
        energenie.finished()
        logger.verbose("Finally finished - must be an error")
        try:
            energenie.cleanup()  # forceably clean up GPIO lines
            logger.verbose("Cleaned up GPIO")
        finally:
            logger.verbose("Could not cleanup GPIO")

# END
