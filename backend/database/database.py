from pymongo import MongoClient

# MongoDB connection
MONGO_URL = "mongodb://localhost:27017/"

client = MongoClient(MONGO_URL)

# DocCrop database
db = client["docrop_db"]

# Collections
farmers_collection = db["farmers"]
crop_analyses_collection = db["crop_analyses"]
followups_collection = db["follow_ups"]
recommendations_collection = db["recommendations"]


# Test MongoDB connection
try:
    client.admin.command("ping")
    print("MongoDB connected successfully!")
except Exception as e:
    print("MongoDB connection failed:", e)