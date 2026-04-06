import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import datetime

app = Flask(__name__)
CORS(app)

# --- MONGODB CLOUD SETUP ---
# Get the connection string from Vercel Environment Variables
MONGO_URI = os.environ.get('MONGO_URI')
client = MongoClient(MONGO_URI)

# Select your database and collection
db = client['sanctuary_db']
health_collection = db['health_logs']

@app.route('/status', methods=['GET'])
def health_check():
    return jsonify({"status": "online", "database": "mongodb_atlas"}), 200

@app.route('/save-data', methods=['POST'])
def save_data():
    data = request.json
    if not data:
        return "No data provided", 400
    
    # Create the document structure
    document = {
        "date": str(datetime.date.today()),
        "steps": data.get('steps', 0),
        "heartRate": data.get('heartRate', 0),
        "sleep": data.get('sleep', 0),
        "timestamp": datetime.datetime.utcnow()
    }
    
    # Insert into MongoDB
    health_collection.insert_one(document)
    return jsonify({"message": "Data saved to Atlas!"}), 201

@app.route('/get-sync', methods=['GET'])
def get_sync():
    # Fetch all logs, sorted by most recent
    logs = list(health_collection.find().sort("timestamp", -1))
    
    # Convert MongoDB ObjectIDs to strings so they can be JSON serialized
    result = []
    for log in logs:
        log['_id'] = str(log['_id'])
        # Convert timestamp to ISO string if needed
        if 'timestamp' in log:
            log['timestamp'] = log['timestamp'].isoformat()
        result.append(log)
        
    return jsonify(result), 200

if __name__ == '__main__':
    app.run(port=5000, debug=True)