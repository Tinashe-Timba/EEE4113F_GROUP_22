# camera imports
import RPi.GPIO as GPIO
from picamera2 import Picamera2
from libcamera import Transform
# python imports
import time
import distutils.util
import xmltodict
from datetime import datetime
video = False
def cam_thread(img_config):
    cam = Picamera2()
    # get configuration parameters
    size  = (int(img_config["width"]), int(img_config["height"]))
    vflip = bool(distutils.util.strtobool(img_config["vflip"]))
    path  = img_config["path"]
    cam_config = cam.create_still_configuration({ "format":img_config["format"],"size":size},transform=Transform(vflip=vflip))

    # apply configuration
    cam.configure(cam_config)
    cam.start()
    # capturing
    i = 0
    while i < 2:
        curr_time = datetime.now()
        file_name = curr_time.strftime("%Y-%m-%d_%H:%M:%S")+".jpg"
        time.sleep(5)
        cam.capture_file(path + file_name)
        # push file_name to processing pipeline
        #queue.put(file_name)
        i = i + 1
def main():
    # data queue
    #q = queue.Queue()
    # load xml file
    LED_PIN = 21
    GPIO.setmode(GPIO.BCM)
    # Set LED_PIN as output
    GPIO.setup(LED_PIN, GPIO.OUT)
    GPIO.output(LED_PIN, GPIO.HIGH)
    xml_handle  = open("/home/mlenka/config.xml","r")
    xml_content = xml_handle.read()
    hashmap = xmltodict.parse(xml_content)
    cam_thread(hashmap["config"]["image"])
    GPIO.cleanup()
if __name__ == "__main__":
    main()
