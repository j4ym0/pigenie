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
