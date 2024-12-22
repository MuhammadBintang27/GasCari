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