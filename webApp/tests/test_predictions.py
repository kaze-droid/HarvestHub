import pytest
from flask import json
import numpy as np
from PIL import Image
from io import BytesIO

# Expected Pass Predictions
@pytest.mark.parametrize("entrylist",
    [
        [np.zeros((1, 31, 31, 1)), "serving_default", "31x31"],
        [np.zeros((1, 128, 128, 1)), "serving_default", "128x128"],
        [255 * np.zeros((1, 31, 31, 1)), "serving_default", "31x31"],
        [255 * np.zeros((1, 128, 128, 1)), "serving_default", "128x128"],
    ])
def test_prediction_form(client, capsys, entrylist):
    url = '/api/predict'
    with capsys.disabled():
        data = {
            "signature_name": entrylist[1],
            "model": entrylist[2],
            "instances": entrylist[0].tolist()
        }

        response = client.get(url, data=json.dumps(data), content_type='application/json')
        # Check if response is 200
        assert response.status_code == 200
        # Check if response is in JSON
        assert response.is_json

# Consistency Testing
@pytest.mark.parametrize("entrylist",
    [
        [[np.zeros((1, 31, 31, 1)), "serving_default", "31x31"],
         [np.zeros((1, 31, 31, 1)), "serving_default", "31x31"],
         [np.zeros((1, 31, 31, 1)), "serving_default", "31x31"], ],
        [[np.zeros((1, 128, 128, 1)), "serving_default", "128x128"],
         [np.zeros((1, 128, 128, 1)), "serving_default", "128x128"],
         [np.zeros((1, 128, 128, 1)), "serving_default", "128x128"], ],
         [[255 * np.zeros((1, 31, 31, 1)), "serving_default", "31x31"],
         [255 * np.zeros((1, 31, 31, 1)), "serving_default", "31x31"],
         [255 * np.zeros((1, 31, 31, 1)), "serving_default", "31x31"], ],
        [[255 * np.zeros((1, 128, 128, 1)), "serving_default", "128x128"],
         [255 * np.zeros((1, 128, 128, 1)), "serving_default", "128x128"],
         [255 * np.zeros((1, 128, 128, 1)), "serving_default", "128x128"], ],

    ]
)
def test_prediction_consistency(client, capsys, entrylist):
    with capsys.disabled():
        url = '/api/predict'
        predictedOutput = []
        for predictions in entrylist:
            data = {
            "signature_name": predictions[1],
            "model": predictions[2],
            "instances": predictions[0].tolist()
        }
            
        response = client.get(url, data=json.dumps(data), content_type='application/json')
        assert response.status_code == 200
        response_body = response.json
        assert response_body['predictions']
        predictedOutput.append(response_body['predictions'])
        # Check if the prediction is consistent
        assert len(predictedOutput) == 1
        # Make sure all the predictions are the same
        assert all(x == predictedOutput[0] for x in predictedOutput) == True



# Expected Fail Predictions
@pytest.mark.xfail(reason="Wrong Input Shape and Wrong Model", strict=True)
@pytest.mark.parametrize("entrylist",
    [
        [np.zeros((1, 32, 32, 1)), "serving_default", "31x31"],
        [np.zeros((1, 31, 31, 1)), "serving_default", "30x30"],
        [np.zeros((1, 128, 128, 1)), "serving_default", "127x127"],
    ])
def test_prediction_form_input_shape(client, capsys, entrylist):
    url = '/api/predict'
    with capsys.disabled():
        data = {
            "signature_name": entrylist[1],
            "model": entrylist[2],
            "instances": entrylist[0].tolist()
        }

        response = client.get(url, data=json.dumps(data), content_type='application/json')
        # Check if response is 200
        assert response.status_code == 200
        # Check if response is in JSON
        assert response.is_json
        # Make sure prediction is in JSON
        assert response.json["predictions"]

# Store Predictions
@pytest.mark.parametrize("entrylist",
    [
        [BytesIO(Image.fromarray(np.zeros((31, 31))).tobytes()).getvalue(), "31x31", "Cauliflower", 99.99],
        [BytesIO(Image.fromarray(np.zeros((128, 128))).tobytes()).getvalue(), "128x128", "Broccoli", 99.99],
        [BytesIO(Image.fromarray(np.zeros((31, 31))).tobytes()).getvalue(), "31x31", "Carrot", 0.00],
        [BytesIO(Image.fromarray(np.zeros((128, 128))).tobytes()).getvalue(), "128x128", "Tomato", 0.00],
    ])
def test_store_predictions(client, capsys, entrylist, signup_user, login_user):
    # Login user
    user_id = login_user.json["id"]

    url = '/api/predict/store'
    with capsys.disabled():
        data = {
            "image": entrylist[0].decode('utf-8'),
            "model": entrylist[1],
            "prediction": entrylist[2],
            "confidence": entrylist[3],
            "user_id": user_id
        }

        res = client.post(url, data=json.dumps(data), content_type='application/json')

        # Check if response is 200
        assert res.status_code == 200
        # Check if response is in JSON
        assert res.is_json


# Store Predictions expected fail
@pytest.mark.xfail(reason="Invalid Image and Invalid Confidence", strict=True)
@pytest.mark.parametrize("entrylist",
    [
        ["This should fail", "31x31", "Cauliflower", 99.99],
        ["So should this", "128x128", "Cauliflower", 99.99],
        [BytesIO(Image.fromarray(np.zeros((31, 31))).tobytes()).getvalue(), "31x31", "Cauliflower", "99.99%"],
        [BytesIO(Image.fromarray(np.zeros((128, 128))).tobytes()).getvalue(), "128x128", "Broccoli", "99.99%"],
    ])
def test_store_prediction_invalid_input(client, capsys, entrylist, signup_user, login_user):
    # Login user
    user_id = login_user.json["id"]

    url = '/api/predict/store'
    with capsys.disabled():
        data = {
            "image": entrylist[0].decode('utf-8'),
            "model": entrylist[1],
            "prediction": entrylist[2],
            "confidence": entrylist[3],
            "user_id": user_id
        }

        res = client.post(url, data=json.dumps(data), content_type='application/json')

        # Check if response is 200
        assert res.status_code == 200
        # Check if response is in JSON
        assert res.is_json

# Store Predictions expected fail
@pytest.mark.xfail(reason="Invalid Image", strict=True)
@pytest.mark.parametrize("entrylist",
    [
        [BytesIO(Image.fromarray(np.zeros((31, 31))).tobytes()).getvalue(), "31x31", "Cauliflower", 99.99],
        [BytesIO(Image.fromarray(np.zeros((128, 128))).tobytes()).getvalue(), "128x128", "Broccoli", 99.99],
        [BytesIO(Image.fromarray(np.zeros((31, 31))).tobytes()).getvalue(), "31x31", "Carrot", 0.00],
        [BytesIO(Image.fromarray(np.zeros((128, 128))).tobytes()).getvalue(), "128x128", "Tomato", 0.00],
    ])
def test_store_prediction_dne_user(client, capsys, entrylist, signup_user, login_user):
    url = '/api/predict/store'
    with capsys.disabled():
        data = {
            "image": entrylist[0].decode('utf-8'),
            "model": entrylist[1],
            "prediction": entrylist[2],
            "confidence": entrylist[3],
            "user_id": -1
        }

        res = client.post(url, data=json.dumps(data), content_type='application/json')

        # Check if response is 200
        assert res.status_code == 200
        # Check if response is in JSON
        assert res.is_json

# Get the predictions
@pytest.mark.parametrize("entrylist",
    [
        [BytesIO(Image.fromarray(np.zeros((31, 31))).tobytes()).getvalue(), "31x31", "Cauliflower", 99.99],
        [BytesIO(Image.fromarray(np.zeros((128, 128))).tobytes()).getvalue(), "128x128", "Broccoli", 99.99],
        [BytesIO(Image.fromarray(np.zeros((31, 31))).tobytes()).getvalue(), "31x31", "Carrot", 0.00],
        [BytesIO(Image.fromarray(np.zeros((128, 128))).tobytes()).getvalue(), "128x128", "Tomato", 0.00],
    ])
def test_get_prediction_real(client, capsys, entrylist, signup_user, login_user):
    # Store some predictions first
    # Login user
    user_id = login_user.json["id"]

    url = '/api/predict/store'
    with capsys.disabled():
        data = {
            "image": entrylist[0].decode('utf-8'),
            "model": entrylist[1],
            "prediction": entrylist[2],
            "confidence": entrylist[3],
            "user_id": user_id
        }

        res = client.post(url, data=json.dumps(data), content_type='application/json')

        # Check if response is 200
        assert res.status_code == 200
        # Check if response is in JSON
        assert res.is_json

        # Get the predictions later on
        url2 = "/api/predict/entries"
        data2 = {
            "user_id": user_id
        }

        res2 = client.get(url2, data=json.dumps(data2), content_type='application/json')

        # Check if response is 200
        assert res2.status_code == 200

        # Check if there is at least one image being returned
        assert len(res2.json['entries']) > 0

# Get predictions for a user with 0 predictions
def test_get_prediction_zero(client, capsys,  signup_user, login_user):
    # Login user
    user_id = login_user.json["id"]

    with capsys.disabled():
        # Get the predictions later on
        url = "/api/predict/entries"
        data = {
            "user_id": user_id
        }

        res = client.get(url, data=json.dumps(data), content_type='application/json')

        # Check if response is 200
        assert res.status_code == 200

        # Check if there is at least one image being returned
        assert len(res.json['entries']) == 0

# Get predictions for a non-existent user
def test_get_prediction_dne(client, capsys):
    with capsys.disabled():
        # Get the predictions later on
        url = "/api/predict/entries"
        data = {
            "user_id": -1
        }

        res = client.get(url, data=json.dumps(data), content_type='application/json')

        # Check if response is 200
        assert res.status_code == 200

        # Check if there is at least one image being returned
        assert len(res.json['entries']) == 0

# Get multiple images made by one user
@pytest.mark.parametrize("entrylist",
    [
        [[BytesIO(Image.fromarray(np.zeros((31, 31))).tobytes()).getvalue(), "31x31", "Cauliflower", 99.99],
        [BytesIO(Image.fromarray(np.zeros((128, 128))).tobytes()).getvalue(), "128x128", "Broccoli", 99.99],
        [BytesIO(Image.fromarray(np.zeros((31, 31))).tobytes()).getvalue(), "31x31", "Carrot", 0.00],
        [BytesIO(Image.fromarray(np.zeros((128, 128))).tobytes()).getvalue(), "128x128", "Tomato", 0.00]],
    ])
def test_bulk_get_images(client, capsys, entrylist, signup_user, login_user):
    user_id = login_user.json["id"]
    url = '/api/predict/store'
    with capsys.disabled():
        for entry in entrylist:
            data = {
                "image": entry[0].decode('utf-8'),
                "model": entry[1],
                "prediction": entry[2],
                "confidence": entry[3],
                "user_id": user_id
            }
            
            res = client.post(url, data=json.dumps(data), content_type='application/json')

        # Get the predictions later on
        url2 = "/api/predict/entries"
        data2 = {
            "user_id": user_id
        }

        res2 = client.get(url2, data=json.dumps(data2), content_type='application/json')

        # Check if response is 200
        assert res2.status_code == 200

        # Check if there are exactly 4 images
        assert len(res2.json['entries']) == 4

        

# Filter predictions for model and vegetable
@pytest.mark.parametrize("entrylist",
    [
        [[BytesIO(Image.fromarray(np.zeros((31, 31))).tobytes()).getvalue(), "31x31", "Cauliflower", 99.99],
        [BytesIO(Image.fromarray(np.zeros((128, 128))).tobytes()).getvalue(), "128x128", "Tomato", 99.99],
        [BytesIO(Image.fromarray(np.zeros((31, 31))).tobytes()).getvalue(), "31x31", "Carrot", 0.00],
        [BytesIO(Image.fromarray(np.zeros((128, 128))).tobytes()).getvalue(), "128x128", "Tomato", 0.00],
        [BytesIO(Image.fromarray(np.zeros((31, 31))).tobytes()).getvalue(), "31x31", "Cauliflower", 99.99],
        [BytesIO(Image.fromarray(np.zeros((128, 128))).tobytes()).getvalue(), "128x128", "Broccoli", 99.99],
        [BytesIO(Image.fromarray(np.zeros((31, 31))).tobytes()).getvalue(), "31x31", "Broccoli", 0.00],
        [BytesIO(Image.fromarray(np.zeros((128, 128))).tobytes()).getvalue(), "128x128", "Tomato", 0.00],
        ["Carrot"], "128x128"],
        [[BytesIO(Image.fromarray(np.zeros((31, 31))).tobytes()).getvalue(), "31x31", "Cauliflower", 99.99],
        [BytesIO(Image.fromarray(np.zeros((128, 128))).tobytes()).getvalue(), "128x128", "Tomato", 99.99],
        [BytesIO(Image.fromarray(np.zeros((31, 31))).tobytes()).getvalue(), "31x31", "Carrot", 0.00],
        [BytesIO(Image.fromarray(np.zeros((128, 128))).tobytes()).getvalue(), "128x128", "Tomato", 0.00],
        [BytesIO(Image.fromarray(np.zeros((31, 31))).tobytes()).getvalue(), "31x31", "Cauliflower", 99.99],
        [BytesIO(Image.fromarray(np.zeros((128, 128))).tobytes()).getvalue(), "128x128", "Broccoli", 99.99],
        [BytesIO(Image.fromarray(np.zeros((31, 31))).tobytes()).getvalue(), "31x31", "Broccoli", 0.00],
        [BytesIO(Image.fromarray(np.zeros((128, 128))).tobytes()).getvalue(), "128x128", "Tomato", 0.00],
        ["Carrot"], "31x31"],
        [[BytesIO(Image.fromarray(np.zeros((31, 31))).tobytes()).getvalue(), "31x31", "Cauliflower", 99.99],
        [BytesIO(Image.fromarray(np.zeros((128, 128))).tobytes()).getvalue(), "128x128", "Tomato", 99.99],
        [BytesIO(Image.fromarray(np.zeros((31, 31))).tobytes()).getvalue(), "31x31", "Carrot", 0.00],
        [BytesIO(Image.fromarray(np.zeros((128, 128))).tobytes()).getvalue(), "128x128", "Tomato", 0.00],
        [BytesIO(Image.fromarray(np.zeros((31, 31))).tobytes()).getvalue(), "31x31", "Cauliflower", 99.99],
        [BytesIO(Image.fromarray(np.zeros((128, 128))).tobytes()).getvalue(), "128x128", "Broccoli", 99.99],
        [BytesIO(Image.fromarray(np.zeros((31, 31))).tobytes()).getvalue(), "31x31", "Broccoli", 0.00],
        [BytesIO(Image.fromarray(np.zeros((128, 128))).tobytes()).getvalue(), "128x128", "Tomato", 0.00],
        ["Carrot", "Tomato"], "128x128"],
        [[BytesIO(Image.fromarray(np.zeros((31, 31))).tobytes()).getvalue(), "31x31", "Cauliflower", 99.99],
        [BytesIO(Image.fromarray(np.zeros((128, 128))).tobytes()).getvalue(), "128x128", "Tomato", 99.99],
        [BytesIO(Image.fromarray(np.zeros((31, 31))).tobytes()).getvalue(), "31x31", "Carrot", 0.00],
        [BytesIO(Image.fromarray(np.zeros((128, 128))).tobytes()).getvalue(), "128x128", "Tomato", 0.00],
        [BytesIO(Image.fromarray(np.zeros((31, 31))).tobytes()).getvalue(), "31x31", "Cauliflower", 99.99],
        [BytesIO(Image.fromarray(np.zeros((128, 128))).tobytes()).getvalue(), "128x128", "Broccoli", 99.99],
        [BytesIO(Image.fromarray(np.zeros((31, 31))).tobytes()).getvalue(), "31x31", "Broccoli", 0.00],
        [BytesIO(Image.fromarray(np.zeros((128, 128))).tobytes()).getvalue(), "128x128", "Tomato", 0.00],
        ["Carrot", "Tomato"], "31x31"],
        [[BytesIO(Image.fromarray(np.zeros((31, 31))).tobytes()).getvalue(), "31x31", "Cauliflower", 99.99],
        [BytesIO(Image.fromarray(np.zeros((128, 128))).tobytes()).getvalue(), "128x128", "Tomato", 99.99],
        [BytesIO(Image.fromarray(np.zeros((31, 31))).tobytes()).getvalue(), "31x31", "Carrot", 0.00],
        [BytesIO(Image.fromarray(np.zeros((128, 128))).tobytes()).getvalue(), "128x128", "Tomato", 0.00],
        [BytesIO(Image.fromarray(np.zeros((31, 31))).tobytes()).getvalue(), "31x31", "Cauliflower", 99.99],
        [BytesIO(Image.fromarray(np.zeros((128, 128))).tobytes()).getvalue(), "128x128", "Broccoli", 99.99],
        [BytesIO(Image.fromarray(np.zeros((31, 31))).tobytes()).getvalue(), "31x31", "Broccoli", 0.00],
        [BytesIO(Image.fromarray(np.zeros((128, 128))).tobytes()).getvalue(), "128x128", "Tomato", 0.00],
        ["Carrot", "Tomato", "Cauliflower", "Broccoli"], "128x128"],
        [[BytesIO(Image.fromarray(np.zeros((31, 31))).tobytes()).getvalue(), "31x31", "Cauliflower", 99.99],
        [BytesIO(Image.fromarray(np.zeros((128, 128))).tobytes()).getvalue(), "128x128", "Tomato", 99.99],
        [BytesIO(Image.fromarray(np.zeros((31, 31))).tobytes()).getvalue(), "31x31", "Carrot", 0.00],
        [BytesIO(Image.fromarray(np.zeros((128, 128))).tobytes()).getvalue(), "128x128", "Tomato", 0.00],
        [BytesIO(Image.fromarray(np.zeros((31, 31))).tobytes()).getvalue(), "31x31", "Cauliflower", 99.99],
        [BytesIO(Image.fromarray(np.zeros((128, 128))).tobytes()).getvalue(), "128x128", "Broccoli", 99.99],
        [BytesIO(Image.fromarray(np.zeros((31, 31))).tobytes()).getvalue(), "31x31", "Broccoli", 0.00],
        [BytesIO(Image.fromarray(np.zeros((128, 128))).tobytes()).getvalue(), "128x128", "Tomato", 0.00],
        ["Carrot", "Tomato", "Cauliflower", "Broccoli"], "31x31"],
    ])
def test_filter_predictions(client, capsys, entrylist, signup_user, login_user):
    user_id = login_user.json["id"]
    url = '/api/predict/store'
    with capsys.disabled():
        for entry in entrylist:
            if type(entry) != list or len(entry) == 0 or type(entry[-1]) != float: continue
            data = {
                "image": entry[0].decode('utf-8'),
                "model": entry[1],
                "prediction": entry[2],
                "confidence": entry[3],
                "user_id": user_id
            }
            
            res = client.post(url, data=json.dumps(data), content_type='application/json')

        # Get the predictions later on
        url2 = "/api/predict/filter"
        data2 = {
            "user_id": user_id,
            "vegetableFilter": entrylist[-2],
            "pastDays": None,
            "modelFilter": entrylist[-1],
            "searchFilter": ""
        }

        res2 = client.get(url2, data=json.dumps(data2), content_type='application/json')

        assert res2.status_code == 200
        for pred in res2.json['entries']:
            assert pred["model"] == entrylist[-1] or pred["prediction"] in entrylist[-2]


# Filter returns nothing
@pytest.mark.parametrize("entrylist",
    [
        [[BytesIO(Image.fromarray(np.zeros((31, 31))).tobytes()).getvalue(), "31x31", "Cauliflower", 99.99],
        [BytesIO(Image.fromarray(np.zeros((128, 128))).tobytes()).getvalue(), "128x128", "Tomato", 99.99],
        [BytesIO(Image.fromarray(np.zeros((31, 31))).tobytes()).getvalue(), "31x31", "Carrot", 0.00],
        [BytesIO(Image.fromarray(np.zeros((128, 128))).tobytes()).getvalue(), "128x128", "Tomato", 0.00],
        [BytesIO(Image.fromarray(np.zeros((31, 31))).tobytes()).getvalue(), "31x31", "Cauliflower", 99.99],
        [BytesIO(Image.fromarray(np.zeros((128, 128))).tobytes()).getvalue(), "128x128", "Broccoli", 99.99],
        [BytesIO(Image.fromarray(np.zeros((31, 31))).tobytes()).getvalue(), "31x31", "Broccoli", 0.00],
        [BytesIO(Image.fromarray(np.zeros((128, 128))).tobytes()).getvalue(), "128x128", "Tomato", 0.00],
        ["Bottle Gourd"], None],
        [[BytesIO(Image.fromarray(np.zeros((31, 31))).tobytes()).getvalue(), "31x31", "Cauliflower", 99.99],
        [BytesIO(Image.fromarray(np.zeros((128, 128))).tobytes()).getvalue(), "128x128", "Tomato", 99.99],
        [BytesIO(Image.fromarray(np.zeros((31, 31))).tobytes()).getvalue(), "31x31", "Carrot", 0.00],
        [BytesIO(Image.fromarray(np.zeros((128, 128))).tobytes()).getvalue(), "128x128", "Tomato", 0.00],
        [BytesIO(Image.fromarray(np.zeros((31, 31))).tobytes()).getvalue(), "31x31", "Cauliflower", 99.99],
        [BytesIO(Image.fromarray(np.zeros((128, 128))).tobytes()).getvalue(), "128x128", "Broccoli", 99.99],
        [BytesIO(Image.fromarray(np.zeros((31, 31))).tobytes()).getvalue(), "31x31", "Broccoli", 0.00],
        [BytesIO(Image.fromarray(np.zeros((128, 128))).tobytes()).getvalue(), "128x128", "Tomato", 0.00],
        ["Bottle Gourd"], None]
    ])
def test_filter_predictions_return_none(client, capsys, entrylist, signup_user, login_user):
    user_id = login_user.json["id"]
    url = '/api/predict/store'
    with capsys.disabled():
        for entry in entrylist:
            if type(entry) != list or len(entry) == 0 or type(entry[-1]) != float: continue
            data = {
                "image": entry[0].decode('utf-8'),
                "model": entry[1],
                "prediction": entry[2],
                "confidence": entry[3],
                "user_id": user_id
            }
            
            res = client.post(url, data=json.dumps(data), content_type='application/json')

        # Get the predictions later on
        url2 = "/api/predict/filter"
        data2 = {
            "user_id": user_id,
            "vegetableFilter": entrylist[-2],
            "pastDays": None,
            "modelFilter": entrylist[-1],
            "searchFilter": ""
        }

        res2 = client.get(url2, data=json.dumps(data2), content_type='application/json')

        assert res2.status_code == 200
        for pred in res2.json['entries']:
            assert pred["model"] == entrylist[-1] or pred["prediction"] in entrylist[-2]

# Test removing prediction entry
@pytest.mark.parametrize("entrylist",
    [
        [BytesIO(Image.fromarray(np.zeros((31, 31))).tobytes()).getvalue(), "31x31", "Cauliflower", 99.99],
        [BytesIO(Image.fromarray(np.zeros((128, 128))).tobytes()).getvalue(), "128x128", "Tomato", 99.99],
        [BytesIO(Image.fromarray(np.zeros((31, 31))).tobytes()).getvalue(), "31x31", "Carrot", 0.00],
        [BytesIO(Image.fromarray(np.zeros((128, 128))).tobytes()).getvalue(), "128x128", "Tomato", 0.00],
        [BytesIO(Image.fromarray(np.zeros((31, 31))).tobytes()).getvalue(), "31x31", "Cauliflower", 99.99],
        [BytesIO(Image.fromarray(np.zeros((128, 128))).tobytes()).getvalue(), "128x128", "Broccoli", 99.99],
        [BytesIO(Image.fromarray(np.zeros((31, 31))).tobytes()).getvalue(), "31x31", "Broccoli", 0.00],
        [BytesIO(Image.fromarray(np.zeros((128, 128))).tobytes()).getvalue(), "128x128", "Tomato", 0.00]
    ])
def test_remove_pred(client, capsys, entrylist, signup_user, login_user):
    # Login user
    user_id = login_user.json["id"]

    url = '/api/predict/store'
    with capsys.disabled():
        data = {
            "image": entrylist[0].decode('utf-8'),
            "model": entrylist[1],
            "prediction": entrylist[2],
            "confidence": entrylist[3],
            "user_id": user_id
        }

        res = client.post(url, data=json.dumps(data), content_type='application/json')

        assert res.status_code == 200
        id = res.json["id"]

        url2 = "/api/predEntry/remove"

        data2 = {
            "id": id
        }

        res2 = client.post(url2, data=json.dumps(data2), content_type='application/json')
        assert res2.status_code == 200
        assert res2.json["id"] == id

# Test removing non-exsistent predictions
@pytest.mark.xfail(reason="Non Existent Entries", strict=True)
@pytest.mark.parametrize("entrylist",
    [
        [-1],
        [4294967296],
        ["Does not exist"],
        [4.20]
    ])
def test_remove_pred_dne(client, capsys, entrylist, signup_user, login_user):
    # Login user
    user_id = login_user.json["id"]

    with capsys.disabled():

        url = "/api/predEntry/remove"

        data = {
            "id": id
        }

        res = client.post(url, data=json.dumps(data), content_type='application/json')
        assert res.status_code == 200
        assert res.json['id']




