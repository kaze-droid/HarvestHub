import pytest
import tensorflow as tf
from tensorflow.keras.preprocessing import image
import requests
import base64
import os
import json
import numpy as numpy

# Test the local server
local_url_31 = 'http://vegetable_server:8501/v1/models/31x31:predict'
local_url_128 = 'http://vegetable_server:8501/v1/models/128x128:predict'

def test_local31x31(load_images, make_prediction):
    data = load_images(31)
    # Get a random image from the images folder
    rand_int = numpy.random.randint(0, len(data))
    img = data[rand_int]
    predictions = make_prediction(img, local_url_31)[0]
    # Make sure the prediction is a list of 10 numbers
    assert isinstance(predictions, list)
    assert len(predictions) == 15
    # Make sure the prediction is a list of floats
    assert isinstance(predictions[0], float)

def test_local128x128(load_images, make_prediction):
    data = load_images(128)
    # Get a random image from the images folder
    rand_int = numpy.random.randint(0, len(data))
    img = data[rand_int]
    predictions = make_prediction(img, local_url_128)[0]
    # Make sure the prediction is a list of 10 numbers
    assert isinstance(predictions, list)
    assert len(predictions) == 15
    # Make sure the prediction is a list of floats
    assert isinstance(predictions[0], float)