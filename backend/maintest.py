from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from datetime import datetime, timezone
import uuid

# 1. Initialize Flask
app = Flask(__name__)
# Paste your Atlas URI here. 
# IMPORTANT: MongoEngine handles the connection automatically using this config.
app.config['MONGO_URI'] =  'mongodb+srv://minip7755_db_user:nx2gI8pqKlOeLEJO@sareefusion.kkwkwcl.mongodb.net/sareefusion?retryWrites=true&w=majority'

mongo = PyMongo(app)
db = mongo.db # This is your database instance

# --- COLLECTIONS ---
# Since we don't use classes, we reference collections directly:
# db.users
# db.assets
# db.designs

@app.route('/')
def index():
    # Test the connection
    return "Connected to MongoDB via Flask-PyMongo!"

# --- USER ROUTES ---

@app.route('/add_user', methods=['POST'])
def add_user():
    data = request.json
    
    # 1. Validate Data manually (since we don't have classes)
    if not data.get('username') :
        return jsonify({"error": "Email and password required"}), 400



    # 3. Create the User Dictionary
    new_user = {
        "public_id": str(uuid.uuid4()),
        "username": data['username'],
        "created_at": datetime.now(timezone.utc)
    }

    # 4. Insert into MongoDB
    db.users.insert_one(new_user)

    return jsonify({"message": "User created", "public_id": new_user['public_id']}), 201

@app.route('/get_user/<username>', methods=['GET'])
def get_user(username):
    # Query the database directly
    user = db.users.find_one({"username": username})
    
    if user:
        # Convert ObjectId to string for JSON compatibility
        user['_id'] = str(user['_id'])
        return jsonify(user), 200
    else:
        return jsonify({"error": "User not found"}), 404

# --- ASSET ROUTES ---

@app.route('/upload_asset', methods=['POST'])
def upload_asset():
    data = request.json
    
    # Example of linking an asset to a user
    user = db.users.find_one({"public_id": data.get('user_public_id')})
    if not user:
        return jsonify({"error": "Invalid User"}), 404

    new_asset = {
        "uuid_name": str(uuid.uuid4()),
        "user_id": user['_id'], # Standard MongoDB Reference (using ObjectId)
        "asset_type": data.get('asset_type'), # border, pallu, or body
        "original_s3_key": data.get('s3_key'),
        "created_at": datetime.now(timezone.utc)
    }
    
    db.assets.insert_one(new_asset)
    
    return jsonify({"message": "Asset Uploaded", "asset_id": new_asset['uuid_name']}), 201

if __name__ == '__main__':
    app.run(debug=True)