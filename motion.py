from gpiozero import MotionSensor
from picamera2 import Picamera2
from datetime import datetime
from time import sleep
from signal import pause
import configparser, subprocess, sys


# Setup
config = configparser.ConfigParser()

try:
    config.read_file(open('settings.cfg'))
except FileNotFoundError:
    print("Could not find settings.cfg", file = sys.stderr)
    sys.exit(1)


# Remote server settings
server_settings = config['server']
server_host = server_settings['host']
server_port = server_settings['port']
server_path = server_settings['path']
server_user = server_settings['user']

# Camera settings
camera_settings = config['camera']
image_path = camera_settings['image_path']
timestamp_format = camera_settings.get('timestamp_format', "%Y-%m-%d_%H.%M.%S")

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
    snapshot_path = f"{image_path}{timestamp}.jpg"
    print("Taking photo", snapshot_path)
    camera.capture_file(snapshot_path)
    print("Captured")
    return snapshot_path


# Upload image to the server
def upload_file(file_path):
    print("Uploading file", file_path, "to", f"{server_user}@{server_host}:{server_path} on {server_port}")
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
