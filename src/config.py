#
# config file
#
# edit this file with your own config defautl should work for most people
#

#
# Genrale stuff for setting up app
#
receive_wait            = 10        # how long to wait for signal before contining code
default_switch_state    = False     # what state all sockets should be in on startup

telemetry               = True      # send some data back to jmoapps, this is not a requirement but helps improve
                                    # set to False if you dont wnat to send any data black
                                    # no personal data will be stored only deviceid, current, voltage and battery
use_smoothing           = True      # if the sockets should use a smoothed watts, this smooths the spikes a troffs
base_watts              = 140       # base watts that are used all the time. you allarm, phone, router smoke detector thay all add up


#
# legacy socket programming
#
#   socket : int    // socket number 1-4 OOK sockets
#   watts : int     // max watts the socket will draw (2Kwh = 2000)
#   max_time : int  // the max time the device should be on in the day
#                   // 0 is none or int in seconds
#
#   priority put the most consuming at the top or the device you want on the most
#
legacy_sockets      = [ {'socket' : 2, 'watts' : 2500, 'max_time' : 3600, 'priority' : 0},
                        {'socket' : 1, 'watts' : 360, 'max_time' : 0, 'priority' : 1}
                      ]
