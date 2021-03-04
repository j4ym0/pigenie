#
# config file
#
# edit this file with your own config defautl should work for most people
#
#
#
# General stuff for setting up app
#
log_level               = 2             # 1 - 4
                                        # 1 warnings and dashboard
                                        # 2 warnings and Information
                                        # 3 warnings, info and debuging
                                        # 4 everything
                                        # 5 everything + timestamp
LOG_FILENAME            = "debug.log"   # filename of the debug logs, use None to disabled
log_to_csv              = False         # will log the results from MIHO004, MIHO005, MIHO006 to CSV
CSV_FILENAME            = "results.csv" # CSV filename for logging, use None to disabled

receive_wait            = 30            # how long to wait for signal before contining code
default_switch_state    = False         # what state all sockets should be in on startup

telemetry               = False         # send some data back to jmoapps, this is not a requirement but helps improve
                                        # set to False if you dont wnat to send any data black
                                        # no personal data will be stored only deviceid, current, voltage and battery

use_smoothing           = True          # if the sockets should use a smoothed watts, this smooths the spikes a troffs in genaration
smoothing_fast_init     = True          # when using smoothing, fast init will backfill the cache with the first value it receives
base_watts              = 100           # base watts that are used all the time. you alarm, phone, router smoke detector thay all add up


#
# legacy socket programming
#
#   description : str // socket description, show in dashboard if set
#   socket : int      // socket number 1-4 OOK sockets
#   watts : int       // max watts the item connected to the socket will draw (2Kwh = 2000)
#   max_time : int    // the max time the device should be on in the day
#                     // 0 is no limit or int in seconds
#
#   priority put the most consuming at the top or the device you want on the most
#
legacy_sockets      = [
                        {'description' : 'Water Heater', 'socket' : 2, 'watts' : 1000, 'max_time' : 7200},
                        {'description' : '', 'socket' : 1, 'watts' : 360, 'max_time' : 0 },
                      ]
