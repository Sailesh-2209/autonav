import cv2
import tensorflow as tf
import matplotlib.pyplot as plt
import os
import random
import glob
import shutil
import time
import numpy as np
import wget
import object_detection
import sys
sys.path.insert(1, "..\\")
from environment import CarlaEnvironment  # noqa

CARLA_PATH = "C:\\Users\\saile\\Desktop\\Sailesh\\Carla Simulator\\CARLA_0.9.10\\WindowsNoEditor\\PythonAPI\\carla\\dist\\carla-*%d.%d-%s.egg"  # noqa

try:
    sys.path.append(glob.glob(CARLA_PATH % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla  # noqa

# -------------------------END OF IMPORTS-------------------------

os.chdir("..")

# -------------------------IMAGE DIMENSIONS-----------------------

IMAGE_DIMENSIONS = [(1080, 1920), (300, 533), (480, 640), (720, 1280)]

# -------------------------CONSTANTS-------------------------------

CUSTOM_MODEL_NAME = "ssd_mobnet_320x320"
PRE_TRAINED_MODEL_NAME = "ssd_mobilenet_v2_fpnlite_320x320_coco17_tpu-8"
PRE_TRAINED_MODEL_URL = "http://download.tensorflow.org/models/object_detection/tf2/20200711/ssd_mobilenet_v2_fpnlite_320x320_coco17_tpu-8.tar.gz"

# -------------------------PATHS AND FILES-------------------------

paths = {
    "WORKSPACE": os.path.join('Object Detection', 'workspace'),
    "TRAIN_IMAGES": os.path.join('Object Detection', 'images', 'train'),
    "TEST_IMAGES": os.path.join('Object Detection', 'images', 'test'),
    "SCRIPTS": os.path.join('Object Detection', 'scripts'),
    "API_MODEL": os.path.join('Object Detection', 'dependencies', 'apimodel'),
    "ANNOTATIONS": os.path.join('Object Detection', 'workspace', 'annotations'),
    "MODELS": os.path.join('Object Detection', 'workspace', 'models'),
    "PRE_TRAINED_MODEL": os.path.join('Object Detection', 'workspace', 'pretrained_models'),
    "CHECKPOINT": os.path.join('Object Detection', 'workspace', 'models', CUSTOM_MODEL_NAME),
    "PROTOC": os.path.join('Object Detection', 'dependencies', 'protoc'),
    "OUTPUT": os.path.join('Object Detection', 'workspace', 'models', CUSTOM_MODEL_NAME, 'export')
}
files = {}


# -------------------------IMAGE COLLECTOR FOR CARLA---------------
class ImageCollector:
    def __init__(self, image_height, image_width):
        self.image_height = image_height
        self.image_width = image_width
        self.labels = ["car", "pole", "pedestrian", "bike", "street_light"]  # noqa
        self.images_path = os.path.join("Object Detection", "images", "collected_images")  # noqa
        self.dump_path = os.path.join("Object Detection", "images", "dump", f"{image_height}x{image_width}")  # noqa
        self.num_images = 10
        self.create_file_paths()

    def create_file_paths(self):
        if not os.path.exists(self.dump_path):
            os.mkdir(self.dump_path)
        else:
            shutil.rmtree(self.dump_path, ignore_errors=True)
            os.mkdir(self.dump_path)
        for label in self.labels:
            path = os.path.join(self.images_path, label)
            if not os.path.exists(path):
                os.mkdir(f"{self.images_path}\\{label}")

    def collect_images(self, image):
        img = np.array(image.raw_data)
        img = img.reshape((self.image_height, self.image_width, 4))
        img = img[:, :, :3]
        cv2.imwrite(f"{self.dump_path}\\{int(time.time())}.jpeg", img)
        cv2.waitKey(1)

    def carla_connect(self):
        vehicle = None
        client = None
        rgb_camera = None
        client = CarlaEnvironment(self.image_height, self.image_width)
        vehicle_blueprint = client.blueprint_library.filter("vehicle.audi.a2")[0]  # noqa
        vehicle = client.world.try_spawn_actor(vehicle_blueprint, random.choice(client.spawn_points))  # noqa
        if vehicle == None:
            print("unable to spawn vehicle")
            return vehicle, client, rgb_camera
        vehicle.set_autopilot(enabled=True)
        client.actor_list.append(vehicle)
        rgb_camera_bp = client.blueprint_library.find('sensor.camera.rgb')
        rgb_camera_bp.set_attribute("image_size_x", f"{self.image_width}")
        rgb_camera_bp.set_attribute("image_size_y", f"{self.image_height}")
        rgb_camera_bp.set_attribute("fov", '110')
        rgb_camera = client.world.try_spawn_actor(rgb_camera_bp, carla.Transform(carla.Location(1, 0, 2)), attach_to=vehicle)  # noqa
        client.actor_list.append(rgb_camera)
        return vehicle, client, rgb_camera


def collect_images(image_height, image_width):
    image_collector = ImageCollector(image_height, image_width)
    vehicle, client, camera = image_collector.carla_connect()
    if vehicle == None:
        print(f"Image collection for {image_width}x{image_height} failed")
        return
    start_time = time.time()
    camera.listen(lambda image: image_collector.collect_images(image))
    while True:
        if time.time() - start_time > 1000:
            break
    client.cleanup()


class Agent:
    def __init__(self):
        print("I am a little agent, short and stout")

    def download_pretrained_model(self):
        wget.download(PRE_TRAINED_MODEL_URL)
        os.system(
            f"move {PRE_TRAINED_MODEL_NAME}.tar.gz {paths['PRE_TRAINED_MODEL']}")
        os.system()


def main():

    # COLLECT IMAGES FROM CARLA
    '''
    for dim in IMAGE_DIMENSIONS:
        image_height, image_width = dim
        print(f"Collecting images for {image_width}x{image_height}")
        collect_images(image_height, image_width)
    '''

    # TRAIN TENSORFLOW MODEL
    agent = Agent()


if __name__ == "__main__":
    main()
