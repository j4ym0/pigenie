# A simple api of connected devices.
#
# NOTE: This is an initial, non persisted implementation only

import time
import requests

telemetry = True

def report_to_api(device):
    # Check if telemetry is turned on
    if not telemetry:
        # No its not
        return
    now = time.time()
    payload = {"timestamp" : time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(now)), "device_id" : device.device_id}
    # List all reading and add to payload, preping for post
    for attr, value in vars(device.readings).items():
        payload[attr] = value
    print ('Payload: %s' % payload)
    postdata(payload)

def postdata(payload=None, iritation = 0):
	try:
		r = requests.post("http://jmoapps.co.uk/pi.php", data=payload)
		print("Posted to web %s" % r)
	except:
		print("Retrying post to web")
		if iritation < 5:
			iritation += 1
			postdata(payload, iritation)

# END
