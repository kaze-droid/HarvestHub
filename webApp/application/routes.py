import os
import numpy as np
import requests
from datetime import datetime, timezone, timedelta
from PIL import Image
import io
import base64

from application import app, db, bcrypt, login_manager
from application.models import User, PredEntry
from application.forms import (
    PredictionForm,
    UserSignUpForm,
    FilterPredForm,
    UserLoginForm,
    UserChangeUsernameForm,
    UserChangePasswordForm,
    UserDeleteAccForm
)

from flask import render_template, request, flash, redirect, send_file, json, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.utils import secure_filename

# Since SGT is 8 hours ahead of UTC, we need to add 8 hours to the time
SGT = timezone(timedelta(hours=8))

login_manager.init_app(app)
# Redirect to login page if user is not logged in
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.route('/')
def index():
    return render_template('index.html', active_page='index', title='Home')

@app.route('/predict', methods=['GET', 'POST'])
@login_required
def predict():
    form = PredictionForm()

    if request.method == "POST":
         if form.validate_on_submit():
            model = form.model.data
            target_height, target_width = model.split('x')
            target_height, target_width = int(target_height), int(target_width)
            if form.imageInput.data:
                img_file = request.files[form.imageInput.name]
                img_array, byte_img = preprocess_image(img_file, target_height, target_width)

            data = {
                "signature_name": "serving_default",
                "instances": img_array.tolist(),
                "model": model
            }

            result, status_code = getPredictAPI(data)

            if status_code != 200:
                flash(result.json['error'], 'danger')
                return redirect(request.url)
            
            prediction_prob = np.array(result.json["predictions"])
            vegetable_class = ['Bean', 'Bitter Gourd', 'Bottle Gourd', 'Brinjal', 'Broccoli', 'Cabbage', 'Capsicum', 'Carrot', 'Cauliflower', 'Cucumber', 'Papaya', 'Potato', 'Pumpkin', 'Radish', 'Tomato']
            prediction = vegetable_class[np.argmax(prediction_prob)]
            
            data = {
                "image": byte_img,
                "model": model,
                "prediction": prediction,
                "confidence": round((np.max(prediction_prob)*100), 2),
                "user_id": current_user.id
            }

            result2, status_code2 = storePredictAPI(data)

            if status_code2 != 200:
                flash(result2.json['error'], 'danger')
                return redirect(request.url)
            
            # Prediction Successful
            flash(f"Predicted Vegetable: {prediction} with {(np.max(prediction_prob)*100):.2f}% confidence", "success")
                        
    return render_template('predict.html', active_page='predict', form=form, title='Predict')

@app.route('/history', methods=["GET", "POST"])
@login_required
def history():
    form = FilterPredForm()
    data = {
        "user_id": current_user.id
    }
    response, status_code = getPredictEntriesAPI(data)
    entries = response.json['entries']
    hasEntries = len(entries) > 0

    if request.method == "POST":
        vegetableFilter = form.vegetableFilter.data
        pastDays = form.pastDays.data
        # Since WTF-Forms returns 'None' as a string, we need to convert it to None
        if pastDays == 'None':
            pastDays = None
        model = form.modelFilter.data
        if model == 'None':
            model = None
        searchFilter = form.searchFilter.data

        data = {
            "user_id": current_user.id,
            "vegetableFilter": vegetableFilter,
            "pastDays": pastDays,
            "modelFilter": model,
            "searchFilter": searchFilter
        }

        response, status_code = filterPredictEntriesAPI(data)
        entries = response.json['entries']  
        hasEntries = True

    return render_template('history.html', active_page='history', title='History', entries=entries, hasEntries=hasEntries, form=form)

# Used for removing entries
@app.route("/removePred", methods=["POST"])
@login_required
def remove():
    # Get the id from the form
    req = request.form
    id = req.get("id")
    data = {
        "id": id
    }
    # Delete the entry
    response, status_code = removePredEntry(data)
    if status_code != 200:
        flash(response.json['error'], 'danger')
        return redirect("/history")
    flash('Prediction removed', 'success')
    # Redirect to history page
    return redirect("/history")

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = UserSignUpForm()

    # If user is already logged in, redirect to profile
    if current_user.is_authenticated:
        return redirect('/profile')

    if request.method == "POST":
        if form.validate_on_submit():
            # Get the form data
            username = form.username.data
            email = form.email.data
            password = form.password.data
            confirmPassword = form.confirmPassword.data
            
            # Add user using internal API
            data = {
                "username": username,
                "email": email,
                "password": password,
                "confirmPassword": confirmPassword
            }

            result, status_code = addUserAPI(data)
            
            if status_code != 200:
                flash(f"Error: {result.json['error']}", 'danger')
                return redirect(request.url)
            
            flash('Account created successfully', 'success')
            return redirect('/login')

    return render_template('signup.html', title='Sign Up', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = UserLoginForm()

    # If user is already logged in, redirect to profile
    if current_user.is_authenticated:
        return redirect('/profile')

    if request.method == "POST":
        if form.validate_on_submit():
            email = form.email.data
            password = form.password.data
            remember = form.remember.data

            data = {
                "email": email,
                "password": password,
                "remember": remember
            }

            # Login using internal API
            response, status_code = loginUserApi(data)

            if status_code != 200:
                flash(f"Error: {response.json['error']}", 'danger')
                return redirect(request.url)
            
            return redirect('/profile')

    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

@app.route('/profile')
@login_required
def profile():
    deleteAccForm = UserDeleteAccForm()
    changePwForm = UserChangePasswordForm()
    changeUserForm = UserChangeUsernameForm()
    return render_template('profile.html', title='Profile', deleteAccForm=deleteAccForm, changePwForm=changePwForm, changeUserForm=changeUserForm)

@app.errorhandler(404)
def page_not_found(e):
    # 'e' is the exception object, which can be used to get the error description
    return (
        render_template(
            "404.html", title="Page Not Found", contentTitle="Page Not Found"
        ),
        404,
    )

@app.route('/deleteAcc', methods=['POST'])
@login_required
def deleteAcc():
    form = UserDeleteAccForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        data = {
            "username": username,
            "password": password
        }

        response, status_code = removeUserApi(data)

        if status_code != 200:
            flash(f"Error: {response.json['error']}", 'danger')
            return redirect('/profile')
        
        return redirect('/')

    else:
        flash('Invalid username or password', 'danger')
        return redirect('/profile')
    
@app.route('/changePassword', methods=['POST'])
@login_required
def changePassword():
    form = UserChangePasswordForm()
    if form.validate_on_submit():
        # Get the form data
        new_password = form.password.data

        data = {
            "password": new_password,
        }

        response, status_code = changePasswordAPI(data)
        if status_code == 200:
            flash("Password changed successfully!", "success")
        else:
            flash("Error changing password!", "error")
    else:
        flash("Passwords do not match!", "error")
    
    # Redirect to profile page
    return redirect("/profile")

@app.route('/changeUsername', methods=['POST'])
@login_required
def changeUsername():
    form = UserChangeUsernameForm()
    if form.validate_on_submit():
        # Get the form data
        new_username = form.username.data

        data = {
            "username": new_username,
        }
        response, status_code = changeUsernameAPI(data)
        if status_code == 200:
            flash("Username changed successfully!", "success")
        else:
            flash("Error changing username!", "error")
    else:
        flash("Username must not contain special characters!", "error")
    
    # Redirect to profile page
    return redirect("/profile")


# API Routes
# Used for predicting the class of an image
@app.route("/api/predict", methods=["GET"])
def getPredictAPI(data=None):
    if data is None:
        data = request.get_json()

    model = data['model']
    predict_url = f"https://vegetablecnn.onrender.com/v1/models/{model}:predict"

    # Remove model from data
    del data['model']
    # Data not in correct format
    if 'instances' not in data or 'signature_name' not in data:
        return jsonify({'error': 'Not Found'}), 404
    headers = {"content-type": "application/json"}

    data = json.dumps(data)

    try:
        json_response = requests.post(predict_url, data=data, headers=headers, timeout=30)
        if json_response.status_code ==  503:
            return jsonify({'error': 'Service Unavailable'}), 503
        predictions = json.loads(json_response.text)['predictions']
        return jsonify({'predictions': predictions}), 200
    # Connection Error
    except (requests.ConnectionError, requests.exceptions.ReadTimeout):
        return jsonify({'error': 'Bad Gateway'}), 502

# Used for storing the prediction in the database
@app.route("/api/predict/store", methods=["POST"])
def storePredictAPI(data=None):
    if data is None:
        data = request.get_json()
        # Convert the image to bytes
        data['image'] = data['image'].encode('utf-8')

    date = datetime.now(SGT)

    new_entry = PredEntry(
        image=data['image'],
        model=data['model'],
        prediction=data['prediction'],
        confidence=data['confidence'],
        prediction_date=date,
        user_id=data['user_id']
    )

    # Make sure user exists
    user = get_entries(User, whereClause=User.id == data['user_id'])

    if user == []:
        return jsonify({'error': 'User does not exist'}),  404

    # Add the entry
    result = add_entry(new_entry)

    if result is None:
        return jsonify({'error': 'Failed to add entry'}),  500
    else:
        # return the result of the db action
        return jsonify({'id': result}), 200
    
# Used for getting the prediction entries
@app.route("/api/predict/entries", methods=["GET"])
def getPredictEntriesAPI(data=None):
    if data is None:
        data = request.get_json()

    user_id = data["user_id"]
    entries = get_entries(PredEntry, whereClause=PredEntry.user_id == user_id)

    entries = [
        {
            "id": entry.id,
            "image": base64.b64encode(entry.image).decode('utf-8'),
            "model": entry.model,
            "prediction": entry.prediction,
            "confidence": entry.confidence,
            "prediction_date": entry.prediction_date.strftime("%d-%b-%Y %H:%M"),
            "user_id": entry.user_id,
        }
        for entry in entries
    ]

    if entries is None:
        return jsonify({'error': 'Failed to get entries'}),  500
    else:
        # Return the entries
        return jsonify({'entries': entries}), 200
    
# Used for filtering the prediction entries
@app.route("/api/predict/filter", methods=["GET"])
def filterPredictEntriesAPI(data=None):
    if data is None:
        data = request.get_json()

    user_id = data["user_id"]
    vegetableFilter = data["vegetableFilter"]
    pastDays = data["pastDays"]
    modelFilter = data["modelFilter"]
    searchFilter = data["searchFilter"]

    where = (PredEntry.user_id == user_id)

    if len(vegetableFilter) > 0:
        where = where & (PredEntry.prediction.in_(vegetableFilter))

    if pastDays:
        # Get the current date
        current_date = datetime.now(SGT)
        # Get the date in the past
        past_date = current_date - timedelta(**{pastDays.split()[1]:int(pastDays.split()[0])})

        where = where & (PredEntry.prediction_date >= past_date)

    if modelFilter:
        where = where & (PredEntry.model == modelFilter)

    if searchFilter:
        where = where & (PredEntry.model.like(f"%{searchFilter}%") | PredEntry.prediction.like(f"%{searchFilter}%") | PredEntry.confidence.like(f"%{searchFilter}%") | PredEntry.prediction_date.like(f"%{searchFilter}%"))
    # Get the entries
    entries = get_entries(PredEntry, whereClause=where)

    if entries is None:
        return jsonify({'error': 'Failed to get entries'}),  500

    entries = [
        {
            "id": entry.id,
            "image": base64.b64encode(entry.image).decode('utf-8'),
            "model": entry.model,
            "prediction": entry.prediction,
            "confidence": entry.confidence,
            "prediction_date": entry.prediction_date.strftime("%d-%b-%Y %H:%M"),
            "user_id": entry.user_id,
        }
        for entry in entries
    ]

    # Return the entries
    return jsonify({'entries': entries}), 200

# Used for removing a prediction entry
@app.route("/api/predEntry/remove", methods=["POST"])
def removePredEntry(data=None):
    if data is None:
        data = request.get_json()

    id = data["id"]
    # Delete the entry
    entry = delete_entry(PredEntry, id)

    if entry is None:
        return jsonify({'error': 'Failed to delete entry'}),  500
    else:
        return jsonify({'id': id}), 200
    
# Used for adding a new user
@app.route("/api/user/add", methods=["POST"])
def addUserAPI(data=None):
    if data is None:
            # Read the json data
            data = request.get_json()

    # Check if the passwords match
    if data["password"] != data["confirmPassword"]:
        return jsonify({'error': 'Passwords do not match'}),  400

    # Hash the password
    hashed_password = bcrypt.generate_password_hash(data["password"])

    # Create the new user
    new_user = User(
        username=data["username"],
        email=data["email"],
        password=hashed_password,
        creation_date=datetime.now(SGT),
    )

    # Add the user
    result = add_entry(new_user)

    if result is None:
        return jsonify({'error': 'Email already exists'}),  401
    else:
        # Return the result of the db action
        return jsonify({'id': result}), 200
    
# Used for getting a user
@app.route("/api/user/login", methods=["POST"])
def loginUserApi(data=None):
    if data is None:
        # Read the json data
        data = request.get_json()

    # Get the user
    user = get_user(data["email"])

    if user is None:
        return jsonify({'error': "Email does not exist"}),  404
    # Check if password is correct (hash from db matches form password)
    elif bcrypt.check_password_hash(user.password, data["password"]):
        login_user(user, remember=data["remember"])
        # Return the json
        return jsonify({"id": user.id}), 200

    else:
        # Return an error
        return jsonify({'error': 'Wrong password'}),  401
    
# Used for removing a user
@app.route("/api/user/remove", methods=["POST"])
def removeUserApi(data=None):
    if data is None:
        # Read the json data
        data = request.get_json()

    # Get id of user
    user = get_user(current_user.email)
    
    if user.username == data["username"] and bcrypt.check_password_hash(user.password, data["password"]):
        # Get all the entries of the user
        entries = get_entries(PredEntry, whereClause=PredEntry.user_id == user.id)
        # Delete all the entries of the user
        for entry in entries:
            delete_entry(PredEntry, entry.id)
        # Delete the user
        result = delete_entry(User, user.id)
        # Logout the user first
        logout_user()

        if result is None:
            return jsonify({'error': 'Failed to delete user'}),  500
        else:
            # Return the result of the db action
            return jsonify({'id': result}), 200
    else:
        return jsonify({'error': 'Wrong username or password'}),  401
    
@app.route('/api/user/changepw', methods=["POST"])
def changePasswordAPI(data=None):
    if data is None:
        data = request.get_json()

    # If not authenticated
    if not current_user.is_authenticated:
        return jsonify({'error': 'Not authenticated'}),  401

     # Get the user (previously validated in login)
    user = get_user(current_user.email)

    # Hash the password
    hashed_password = bcrypt.generate_password_hash(data["password"])

    # Update the password
    user = update_user(user, password=hashed_password)
    
    if user is None:
        # Return an error
        return jsonify({'error': 'Failed to update password'}),  500
    else:
        # Return the result of the db action
        return jsonify({'id': user.id}), 200
    
@app.route('/api/user/changeuser', methods=["POST"])
def changeUsernameAPI(data=None):
    if data is None:
        # Read the json data
        data = request.get_json()

    # If not authenticated
    if not current_user.is_authenticated:
        return jsonify({'error': 'Not authenticated'}),  401

    # Get the user (previously validated in login)
    user = get_user(current_user.email)

    # Update the username
    user = update_user(user, username=data["username"])

    if user is None:
        # Return an error
        return jsonify({'error': 'Failed to update username'}),  500
    else:
        # Return the result of the db action
        return jsonify({'id': user.id}), 200

# Helper Functions
def add_entry(new_entry):
    try:
        db.session.add(new_entry)
        db.session.commit()
        return new_entry.id
    except Exception as e:
        db.session.rollback()
        return None
    
def get_entries(model, whereClause=True):
    try:
        entries = (
            db.session.execute(db.select(model).where(whereClause).order_by(model.id))
            .scalars()
            .all()
        )
        return entries
    except Exception as e:
        db.session.rollback()
        return None
    
def delete_entry(model, id):
    try:
        entry = db.get_or_404(model, id)
        db.session.delete(entry)
        db.session.commit()
        return entry.id
    except Exception as e:
        db.session.rollback()
        return None
    
def get_user(email):
    try:
        user = db.session.query(User).filter_by(email=email).first_or_404()
        return user
    except Exception as e:
        return None
    
def update_user(user, username=None, password=None):
    try:
        if username:
            user.username = username
        if password:
            user.password = password
        db.session.commit()
        return user
    except Exception as e:
        db.session.rollback()
        return None
    
def preprocess_image(file, target_height, target_width):
            img = Image.open(file)
            # Convert to grayscale
            img = img.convert('L')
            # Resize image
            img = img.resize(size=(target_height, target_width))
            # Convert to array and standardise it
            img_array = np.array(img)

            # Reshape the image to (1, img_size, img_size, 1)
            img_array = img_array.reshape(1, target_height, target_width, 1)

            # Convert byte
            image_io = io.BytesIO()
            img.save(image_io, format='PNG')
            byte_img = image_io.getvalue()

            return img_array, byte_img