import os
import re
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
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

# Fungsi membaca dokumen dari koleksi processed
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
                "title": doc.get("judul", ""),
                "url": doc.get("url", ""),
                "img_url": doc.get("image_url", ""),
                "tanggalberita": doc.get("date", ""),
                "snippet": doc.get("content", "")[:200]
            })

        return documents
    except Exception as e:
        print(f"Error reading from scrapping database: {e}")
        return []

# Fungsi menghitung Cosine Similarity
def calculate_cosine_similarity(query, documents):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents + [query])
    return cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1]).flatten()

# Fungsi menghitung Jaccard Similarity
def calculate_jaccard_similarity(query, documents):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents)
    query_tfidf = vectorizer.transform([query])

    binary_matrix = (tfidf_matrix > 0).astype(int)
    query_binary = (query_tfidf > 0).astype(int)

    scores = []
    for i in range(binary_matrix.shape[0]):
        intersection = np.logical_and(query_binary.toarray(), binary_matrix[i].toarray()).sum()
        union = np.logical_or(query_binary.toarray(), binary_matrix[i].toarray()).sum()
        scores.append(intersection / union if union != 0 else 0)
    return scores

# Fungsi untuk mengambil snippet dokumen
def extract_snippet(document, query, max_length=200):
    start_index = document.lower().find(query.lower())
    if start_index == -1:
        start_index = 0

    end_index = start_index + max_length
    if end_index < len(document):
        last_space = document.rfind(" ", start_index, end_index)
        if last_space != -1:
            end_index = last_space

    snippet = document[start_index:end_index]
    return snippet.strip() + ("..." if len(document) > end_index else "")

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
                    "img_url": doc["img_url"],
                    "tanggalberita": doc["tanggalberita"],
                    "snippet": doc["snippet"]
                })

    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
