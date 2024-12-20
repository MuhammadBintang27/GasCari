import re
from pymongo import MongoClient
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from nltk.tokenize import word_tokenize
import nltk
from datetime import datetime

# Unduh resource tokenisasi NLTK
nltk.download('punkt')

# Koneksi ke MongoDB
client = MongoClient("mongodb://localhost:27017/")
source_db = client["scrapping"]  # Database asal
processed_db = client["processed"]  # Database untuk hasil yang diproses

# Inisialisasi stopwords dari Sastrawi
stopword_factory = StopWordRemoverFactory()
stopwords = set(stopword_factory.get_stop_words())

# Tambahan stopwords dari file stopword.txt
with open("stopword.txt", "r") as file:
    additional_stopwords = set(file.read().splitlines())
stopwords.update(additional_stopwords)

# Inisialisasi stemming dari Sastrawi
stemmer_factory = StemmerFactory()
stemmer = stemmer_factory.create_stemmer()

# Fungsi cleaning text
def clean_text(text):
    text = re.sub(r"http\S+|www\S+|https\S+", "", text)  # Hapus URL
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)  # Hapus karakter non-alfanumerik
    text = text.lower().strip()  # Ubah ke lowercase dan hapus spasi di awal/akhir
    return text

# Fungsi untuk tokenisasi, stopword removal, dan stemming
def tokenize_stem_and_remove_stopwords(text):
    # Tokenisasi menggunakan NLTK
    tokens = word_tokenize(text)
    # Filter stopwords dan token dengan panjang > 2 karakter
    filtered_tokens = [token for token in tokens if token not in stopwords and len(token) > 2]
    # Proses stemming menggunakan Sastrawi
    stemmed_tokens = [stemmer.stem(token) for token in filtered_tokens]
    return stemmed_tokens

# Proses data dari setiap koleksi
collections = ["all", "berita", "mobil", "motorrace", "motor"]
for collection_name in collections:
    print(f"[{datetime.now()}] Memproses koleksi '{collection_name}'...")  # Log awal koleksi
    source_collection = source_db[collection_name]
    processed_collection = processed_db[collection_name]  # Koleksi di database "processed"
    
    # Hapus data lama di koleksi tujuan (opsional, agar tidak terjadi duplikasi)
    deleted_count = processed_collection.delete_many({}).deleted_count
    print(f"[{datetime.now()}] Koleksi '{collection_name}': {deleted_count} dokumen lama dihapus.")  # Log penghapusan
    
    documents = source_collection.find()
    total_docs = source_collection.count_documents({})
    processed_count = 0
    
    for doc in documents:
        # Gabungkan title dan content
        combined_text = f"{doc.get('title', '')} {doc.get('content', '')}"
        
        # Cleaning text
        cleaned_text = clean_text(combined_text)
        
        # Tokenisasi, stemming, dan stopword removal
        tokens = tokenize_stem_and_remove_stopwords(cleaned_text)
        
        # Simpan hasil ke database "processed"
        processed_collection.insert_one({
            "original_id": doc["_id"],
            "processed_text": tokens,
            "date_added": doc.get("date_added")
        })
        
        processed_count += 1
        if processed_count % 100 == 0:  # Log setiap 100 dokumen
            print(f"[{datetime.now()}] Koleksi '{collection_name}': {processed_count}/{total_docs} dokumen diproses.")
    
    # Log selesai untuk koleksi ini
    print(f"[{datetime.now()}] Koleksi '{collection_name}' selesai. Total dokumen diproses: {processed_count}/{total_docs}.")

print(f"[{datetime.now()}] Semua proses selesai. Hasil tersimpan di database 'processed'.")
import re
from pymongo import MongoClient
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from nltk.tokenize import word_tokenize
import nltk
from datetime import datetime

# Unduh resource tokenisasi NLTK
nltk.download('punkt')

# Koneksi ke MongoDB
client = MongoClient("mongodb://localhost:27017/")
source_db = client["scrapping"]  # Database asal
processed_db = client["processed"]  # Database untuk hasil yang diproses

# Inisialisasi stopwords dari Sastrawi
stopword_factory = StopWordRemoverFactory()
stopwords = set(stopword_factory.get_stop_words())

# Tambahan stopwords dari file stopword.txt
with open("stopword.txt", "r") as file:
    additional_stopwords = set(file.read().splitlines())
stopwords.update(additional_stopwords)

# Inisialisasi stemming dari Sastrawi
stemmer_factory = StemmerFactory()
stemmer = stemmer_factory.create_stemmer()

# Fungsi cleaning text
def clean_text(text):
    text = re.sub(r"http\S+|www\S+|https\S+", "", text)  # Hapus URL
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)  # Hapus karakter non-alfanumerik
    text = text.lower().strip()  # Ubah ke lowercase dan hapus spasi di awal/akhir
    return text

# Fungsi untuk tokenisasi, stopword removal, dan stemming
def tokenize_stem_and_remove_stopwords(text):
    # Tokenisasi menggunakan NLTK
    tokens = word_tokenize(text)
    # Filter stopwords dan token dengan panjang > 2 karakter
    filtered_tokens = [token for token in tokens if token not in stopwords and len(token) > 2]
    # Proses stemming menggunakan Sastrawi
    stemmed_tokens = [stemmer.stem(token) for token in filtered_tokens]
    return stemmed_tokens

# Proses data dari setiap koleksi
collections = ["all", "berita", "mobil", "motorrace", "motor"]
for collection_name in collections:
    print(f"[{datetime.now()}] Memproses koleksi '{collection_name}'...")  # Log awal koleksi
    source_collection = source_db[collection_name]
    processed_collection = processed_db[collection_name]  # Koleksi di database "processed"
    
    # Hapus data lama di koleksi tujuan (opsional, agar tidak terjadi duplikasi)
    deleted_count = processed_collection.delete_many({}).deleted_count
    print(f"[{datetime.now()}] Koleksi '{collection_name}': {deleted_count} dokumen lama dihapus.")  # Log penghapusan
    
    documents = source_collection.find()
    total_docs = source_collection.count_documents({})
    processed_count = 0
    
    for doc in documents:
        # Gabungkan title dan content
        combined_text = f"{doc.get('title', '')} {doc.get('content', '')}"
        
        # Cleaning text
        cleaned_text = clean_text(combined_text)
        
        # Tokenisasi, stemming, dan stopword removal
        tokens = tokenize_stem_and_remove_stopwords(cleaned_text)
        
        # Simpan hasil ke database "processed"
        processed_collection.insert_one({
            "original_id": doc["_id"],
            "processed_text": tokens,
            "date_added": doc.get("date_added")
        })
        
        processed_count += 1
        if processed_count % 100 == 0:  # Log setiap 100 dokumen
            print(f"[{datetime.now()}] Koleksi '{collection_name}': {processed_count}/{total_docs} dokumen diproses.")
    
    # Log selesai untuk koleksi ini
    print(f"[{datetime.now()}] Koleksi '{collection_name}' selesai. Total dokumen diproses: {processed_count}/{total_docs}.")

print(f"[{datetime.now()}] Semua proses selesai. Hasil tersimpan di database 'processed'.")
