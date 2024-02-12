import pytest
import os
import tensorflow as tf
from tensorflow.keras.preprocessing import image
import requests
import base64
import json
import numpy as numpy

# Load all the images from the images folder
@pytest.fixture
def load_images():
    def inner_load_images(img_size):
        path = os.path.join(os.getcwd(), 'DLModel/tests/images/train')
        images = []
        for file in os.listdir(path):
            img = image.img_to_array(image.load_img(os.path.join(path, file), color_mode="grayscale", target_size=(img_size, img_size))) / 255.
            # Reshape the image to (1, img_size, img_size, 1)
            img = img.reshape(1, img_size, img_size, 1)
            images.append(img)
        return images

    return inner_load_images

# Make prediction
@pytest.fixture
def make_prediction():
    def inner_make_prediction(instances, url):
        # Send a request using JSON format to the server and retrieve the prediction
        data = json.dumps({"signature_name": "serving_default", "instances": instances.tolist()})
        headers = {"content-type": "application/json"}
        json_response = requests.post(url, data=data, headers=headers)
        predictions = json.loads(json_response.text)['predictions']
        return predictions

    return inner_make_prediction