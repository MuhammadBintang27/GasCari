import os
import re
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from functions.document_handler import read_documents_from_processed, read_documents_from_scrapping
from functions.query_prepocessing import clean_query
from functions.similarity import calculate_cosine_similarity, calculate_jaccard_similarity
from functions.snippet import extract_snippet
import numpy as np

# Inisialisasi Flask dan PyMongo
app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/"  # Ganti dengan URI MongoDB Anda
CORS(app, origins="http://localhost:5173", methods=["GET", "POST"], allow_headers=["Content-Type", "Authorization"])

mongo = PyMongo(app)

# Konstanta database dan koleksi
DB_SCRAPPING = "scrapping"
DB_PROCESSED = "processed"
COLLECTIONS = ["all", "berita", "mobil", "motor", "motorrace"]

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
    app.run(debug=True)
