from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from functions.similarity import calculate_cosine_similarity, calculate_jaccard_similarity
from functions.snippet import extract_snippet
from flask_cors import CORS

# Inisialisasi Flask dan PyMongo
app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/"  # Ganti dengan URI MongoDB Anda
CORS(app, origins="http://localhost:5173", methods=["GET", "POST"], allow_headers=["Content-Type", "Authorization"])

mongo = PyMongo(app)

# Nama database dan koleksi
DB_SCRAPPING = "scrapping"
DB_PROCESSED = "processed"

COLLECTIONS = ["all", "berita", "mobil", "motor", "motor_race"]

@app.route('/search', methods=['POST'])
def search():
    """Endpoint untuk mencari dokumen berdasarkan kategori, scoring, dan query."""
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

    # Membaca dokumen dari MongoDB (processed)
    output_documents, titles = read_documents_from_processed(category)

    # Membaca dokumen dari MongoDB (scrapping)
    input_documents = read_documents_from_scrapping(category)

    if not output_documents:
        return jsonify({"error": "No documents found in the selected category"}), 404

    # Menghitung skor berdasarkan metode yang dipilih
    if scoring == "cosine":
        scores = calculate_cosine_similarity(query, output_documents)
    else:
        scores = calculate_jaccard_similarity(query, output_documents)

    # Filter dokumen dengan skor > 0
    valid_indices = [i for i, score in enumerate(scores) if score > 0]
    results = [
        {
            "title": titles[i],
            "score": scores[i],
            "snippet": extract_snippet(output_documents[i], query)
        }
        for i in valid_indices
    ]

    # Perkaya hasil dengan data dari scrapping
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

def read_documents_from_processed(category):
    """Membaca dokumen dari koleksi processed berdasarkan kategori."""
    collection = mongo.db[DB_PROCESSED][category]  # Akses koleksi di database processed
    documents = []
    titles = []

    for doc in collection.find():
        processed_text = doc.get("processed_text", [])
        if processed_text:
            documents.append(" ".join(processed_text))
            titles.append(doc.get("title", ""))
    
    return documents, titles

def read_documents_from_scrapping(category):
    """Membaca dokumen dari koleksi scrapping berdasarkan kategori."""
    collection = mongo.db[DB_SCRAPPING][category]  # Akses koleksi di database scrapping
    documents = []

    for doc in collection.find():
        documents.append({
            "title": doc.get("title", ""),
            "url": doc.get("url", ""),
            "img_url": doc.get("image_url", ""),
            "tanggalberita": doc.get("date", ""),
            "snippet": doc.get("content", "")[:200]  # Ambil snippet dari content
        })
    
    return documents

if __name__ == '__main__':
    app.run(debug=True)
