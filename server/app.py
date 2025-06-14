import os
import re
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scoring.functions.query_prepocessing import clean_query
from scoring.functions.similarity import calculate_cosine_similarity, calculate_jaccard_similarity
from scoring.functions.snippet import extract_snippet
import numpy as np
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Constants
DB_PROCESSED = "processed"
DB_SCRAPPING = "scrapping"

# Inisialisasi Flask dan PyMongo
app = Flask(__name__)
CORS(app)

# Configure MongoDB connection
app.config["MONGO_URI"] = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
mongo = PyMongo(app)

# Konstanta database dan koleksi
COLLECTIONS = ["all", "berita", "mobil", "motor", "motorrace"]

def read_documents_from_processed(category):
    try:
        collection = mongo.cx[DB_PROCESSED][category]
        documents = []
        titles = []

        cursor = collection.find({})
        for doc in cursor:
            processed_text = doc.get("processed_text", [])
            documents.append(" ".join(processed_text))
            titles.append(doc.get("title", "Unknown Title"))

        return documents, titles
    except Exception as e:
        print(f"Error reading from processed database: {e}")
        return [], []

# Fungsi membaca dokumen dari koleksi scrapping
def read_documents_from_scrapping(category):
    try:
        collection = mongo.cx[DB_SCRAPPING][category]
        documents = []

        cursor = collection.find({})
        for doc in cursor:
            documents.append({
                "title": doc.get("title", ""),
                "url": doc.get("url", ""),
                "image_url": doc.get("image_url", ""),
                "date": doc.get("date", ""),
                "snippet": doc.get("content", "")[:200]
            })

        return documents
    except Exception as e:
        print(f"Error reading from scrapping database: {e}")
        return []

# Endpoint untuk mengecek koneksi MongoDB
@app.route('/', methods=['GET'])
def check_connection():
    try:
        # Mencoba mengakses server info untuk memastikan koneksi berhasil
        server_info = mongo.cx.server_info()
        
        # Mendapatkan daftar database
        database_list = mongo.cx.list_database_names()
        
        # Mengecek keberadaan database yang dibutuhkan
        db_status = {
            "processed": DB_PROCESSED in database_list,
            "scrapping": DB_SCRAPPING in database_list
        }
        
        # Mengecek koleksi dalam database
        collections_status = {}
        if DB_PROCESSED in database_list:
            processed_collections = mongo.cx[DB_PROCESSED].list_collection_names()
            collections_status["processed"] = processed_collections
        if DB_SCRAPPING in database_list:
            scrapping_collections = mongo.cx[DB_SCRAPPING].list_collection_names()
            collections_status["scrapping"] = scrapping_collections

        return jsonify({
            "status": "success",
            "message": "MongoDB Atlas connection successful",
            "server_info": {
                "version": server_info.get("version"),
                "host": server_info.get("host"),
                "port": server_info.get("port")
            },
            "environment": {
                "mongodb_uri": os.getenv("MONGODB_URI", "mongodb://localhost:27017/"),
                "db_processed": DB_PROCESSED,
                "db_scrapping": DB_SCRAPPING
            },
            "database_status": {
                "available_databases": database_list,
                "required_databases": db_status,
                "collections": collections_status
            }
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"MongoDB connection failed: {str(e)}",
            "environment": {
                "mongodb_uri": os.getenv("MONGODB_URI", "mongodb://localhost:27017/"),
                "db_processed": DB_PROCESSED,
                "db_scrapping": DB_SCRAPPING
            }
        }), 500

# Endpoint untuk pencarian
@app.route('/search', methods=['POST'])
def search():
    data = request.json
    category = data.get('category')
    scoring = data.get('scoring')
    query = data.get('query')

    if category not in COLLECTIONS:
        return jsonify({"error": "Invalid category"}), 400

    if scoring not in ["cosine", "jaccard"]:
        return jsonify({"error": "Invalid scoring method"}), 400

    if not query:
        return jsonify({"error": "Query cannot be empty"}), 400

    output_documents, titles = read_documents_from_processed(category)
    input_documents = read_documents_from_scrapping(category)
    query = clean_query(query)

    if not output_documents:
        return jsonify({"error": "No documents found in the selected category"}), 404

    if scoring == "cosine":
        scores = calculate_cosine_similarity(query, output_documents)
    else:
        scores = calculate_jaccard_similarity(query, output_documents)

    valid_indices = [i for i, score in enumerate(scores) if score > 0]
    results = [
        {
            "title": titles[i],
            "score": scores[i],
            "snippet": extract_snippet(output_documents[i], query)
        }
        for i in valid_indices
    ]

    for result in results:
        for doc in input_documents:
            if result["title"] == doc["title"]:
                result.update({
                    "url": doc["url"],
                    "image_url": doc["image_url"],
                    "date": doc["date"],
                    "snippet": doc["snippet"]
                })

    return jsonify(results)
if __name__ == '__main__':
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
