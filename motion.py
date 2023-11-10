from picamera2 import Picamera2
from datetime import datetime
from time import sleep
from signal import pause

# Setup
timestamp_format = "%Y-%m-%d_%H.%M.%S"

print("Setting up PIR...")
pir = MotionSensor(4)
print("..done")

print("Starting camera...")
camera = Picamera2()

# Set camera options
camera_config = camera.create_still_configuration(main={"size": (3280, 2464)}, lores={"size": (1920, 1080)}, display="lores")
camera.configure(camera_config)

camera.start()
print("..done")

def take_photo():
    now = datetime.now()
    timestamp = now.strftime(timestamp_format)
    print("Taking photo", timestamp)
    camera.capture_file('/home/pi/motion/images/%s.jpg' % timestamp)
    print("Captured")
    sleep(5)


try:
    print("Motion detection ready")
    while True:
        pir.when_motion = take_photo
except KeyboardInterrupt:
    print("Exiting motion")
    pir.when_motion = None
    camera.close()
