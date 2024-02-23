import time
import logging
from poe import POE_HAT_B

logging.basicConfig(level=logging.INFO)

POE = POE_HAT_B()

try:
    while 1:
        POE.display()
        time.sleep(1)

except KeyboardInterrupt:
    print("ctrl + c:")
    POE.disable_fan()
