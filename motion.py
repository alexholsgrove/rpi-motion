from gpiozero import MotionSensor
from picamera2 import Picamera2
from datetime import datetime
from time import sleep
from signal import pause
#from libcamera import controls
import configparser, os, subprocess, sys


# Setup
config = configparser.ConfigParser()

try:
    config.read(os.path.join(os.path.dirname(__file__), 'settings.cfg'))
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

# Motion settings
interval = int(config['motion'].getint('interval', 5));
start_time = datetime.strptime(config['motion'].get('start_time', '08:00'), '%H:%M').time()
end_time = datetime.strptime(config['motion'].get('end_time', '18:00'), '%H:%M').time()

print("Setting up PIR...")
pir = MotionSensor(4)
print("..done")

print("Starting camera...")
camera = Picamera2()

# Set camera options
camera_config = camera.create_still_configuration(main={"size": (3280, 2464)}, lores={"size": (1920, 1080)}, display="lores")
camera.configure(camera_config)

camera.start()
#camera.set_controls({"AfMode": controls.AfModeEnum.Continuous})
print("..done")


# Capture a photo
def take_photo():
    now = datetime.now()
    timestamp = now.strftime(timestamp_format)
    snapshot_path = f"{image_path}{timestamp}.jpg"
    print("Taking photo", snapshot_path)
    #camera.autofocus_cycle()
    camera.capture_file(snapshot_path)
    print("Captured")
    return snapshot_path


# Upload image to the server
def upload_file(file_path):
    print("Uploading file", file_path, "to", f"{server_user}@{server_host}:{server_path} on {server_port}")
    subprocess.run(["scp", "-O", "-P", server_port, file_path, f"{server_user}@{server_host}:{server_path}"])


# Callback function for motion detected
def motion_detected():
    if start_time <= datetime.now().time() <= end_time:
        image_capture = take_photo()
        upload_file(image_capture)
    else:
        print("Motion detected, but outside start/end time")
    sleep(interval)


try:
    print("Motion detection ready")
    while True:
        pir.when_motion = motion_detected
except KeyboardInterrupt:
    print("Exiting motion")
    pir.when_motion = None
    camera.close()
