import base64
import os
import django
import sys
import requests
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from django.contrib.auth.hashers import make_password

app = Flask(__name__)
CORS(app)

# ✅ Fix the BASE_DIR to ensure Django is found
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(BASE_DIR)  # ✅ Ensure Django is inside Python path

# ✅ Explicitly add webapp and dvwa
sys.path.append(os.path.join(BASE_DIR, "webapp"))
sys.path.append(os.path.join(BASE_DIR, "dvwa"))

# ✅ Correct Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dvwa.settings")  

# ✅ Now Django should initialize correctly
django.setup()


app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'db.sqlite3')}" # set the database URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # disable the modification tracking
db = SQLAlchemy(app) # initialise the database

# defining User model to query the auth_user table
class User(db.Model):
    __tablename__ = 'auth_user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=True)

# API endpoints
# get user data based on user_id
@app.route('/api/user_data', methods=['GET'])
def get_user_data():
    user_id = request.args.get("user_id")

    if not user_id:
        return jsonify({"error": "Missing user_id parameter"}), 400 # Bad request

    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404 # Not found

    response_data = {
        "id": user.id,
        "username": user.username,
        "email": user.email  # data exposed!
    }

    # If accessing user id 1, get the flag for exercise 4
    if str(user_id) == "1":
        flag_response = requests.post(
            "https://api-dvwa.onrender.com/api/get_flag",
            json={"exercise": "4"}
        )
        if flag_response.status_code == 200:
            response_data["flag"] = flag_response.json().get("flag")

    return jsonify(response_data)

# reset password based on user_id and new_password
@app.route('/api/reset_password', methods=['POST'])
def reset_password():
    data = request.json
    user_id = data.get("user_id")
    new_password = data.get("new_password")

    if not user_id or not new_password:
        return jsonify({"message": "Missing parameters", "status": "error"}), 400 # Bad request

    user_id = base64.b64decode(user_id).decode('utf-8')  # decode the base64 encoded user_id

    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({"message": "User not found", "status": "error"}), 404

    # update user password based on django password hashing
    user.password = make_password(new_password)
    db.session.commit()

    return jsonify({
        "message": f"Password reset successful for {user.username}",
        "status": "success",
        "username": user.username  # included for determining flag in front end
    })

# run the app on port 5000
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)  # Allow connections from other containers



