import time
import logging
from poe import POE_HAT_B

logging.basicConfig(level=logging.INFO)

POE = POE_HAT_B()

try:
    while 1:
        POE.POE_HAT_Display(30)
        time.sleep(1)

except KeyboardInterrupt:
    print("ctrl + c:")
    POE.FAN_OFF()
