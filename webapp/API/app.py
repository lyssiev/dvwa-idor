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

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dvwa.settings")
django.setup()

app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'db.sqlite3')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# defining User model to query the auth_user table
class User(db.Model):
    __tablename__ = 'auth_user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=True)
    
@app.route('/api/user_data', methods=['GET'])
def get_user_data():
    user_id = request.args.get("user_id")
    current_user_id = request.args.get("current_user_id")  # Simulate logged-in user ID

    if not user_id:
        return jsonify({"error": "Missing user_id parameter"}), 400

    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    response_data = {
        "id": user.id,
        "username": user.username,
        "email": user.email  # data exposed!
    }

    # iF request sent from a different user, get the flag
    if current_user_id and str(current_user_id) != str(user_id):
        flag_response = requests.post(
            "https://api-dvwa.onrender.com/api/get_flag",
            json={"exercise": "4"}
        )
        if flag_response.status_code == 200:
            response_data["flag"] = flag_response.json().get("flag")

    return jsonify(response_data)


@app.route('/api/reset_password', methods=['POST'])
def reset_password():
    data = request.json
    user_id = data.get("user_id")
    new_password = data.get("new_password")

    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({"message": "User not found", "status": "error"}), 404

    # update user password based on django password hashing
    user.password = make_password(new_password)
    db.session.commit()

    return jsonify({
        "message": f"Password reset successful for {user.username}",
        "status": "success",
        "username": user.username # included for determining flag in front end
    })


    

if __name__ == '__main__':
    app.run(debug=False, port=5000)



