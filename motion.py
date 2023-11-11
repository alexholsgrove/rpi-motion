from gpiozero import MotionSensor
from picamera2 import Picamera2
from datetime import datetime
from time import sleep
from signal import pause
import subprocess

# Setup
server_host = ""
server_port = "23"
server_path = ""
server_user = ""

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


# Capture a photo
def take_photo():
    now = datetime.now()
    timestamp = now.strftime(timestamp_format)
    image_path = f"/home/pi/scripts/rpi-motion/images/{timestamp}.jpg"
    print("Taking photo", image_path)
    camera.capture_file(image_path)
    print("Captured")
    return image_path


# Upload image to the server
def upload_file(file_path):
    print("Uploading file", file_path)
    subprocess.run(["scp", "-O", "-P", server_port, file_path, f"{server_user}@{server_host}:{server_path}"])


# Callback function for motion detected
def motion_detected():
    image_capture = take_photo()
    upload_file(image_capture)


try:
    print("Motion detection ready")
    while True:
        pir.when_motion = motion_detected
except KeyboardInterrupt:
    print("Exiting motion")
    pir.when_motion = None
    camera.close()