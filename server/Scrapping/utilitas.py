from pymongo import MongoClient
import os
import json

# Membuat koneksi ke MongoDB
client = MongoClient("mongodb://localhost:27017/")  # Gantilah URL jika menggunakan server MongoDB remote
db = client["Scrapping"]

def save_to_mongo(category, data):
    """
    Menyimpan data ke dalam collection MongoDB berdasarkan kategori yang diberikan.
    Format data yang diterima adalah { "judul_file.txt": "url" }
    """
    collection = db[category]  # Menggunakan nama kategori sebagai nama collection

    # Menggunakan upsert untuk menambahkan atau memperbarui data jika sudah ada
    for title, url in data.items():
        collection.update_one(
            {"judul": title},  # Menentukan filter untuk data yang sudah ada
            {"$set": {"url": url}},  # Mengupdate atau menyimpan URL baru
            upsert=True  # Jika tidak ada, maka data akan dimasukkan
        )

def update_json(file_path, data):
    """
    Memperbarui file JSON dengan data baru. 
    Format data baru adalah { "judul_file.txt": "url" }
    """
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
    else:
        existing_data = {}

    # Gabungkan data baru ke data yang ada
    existing_data.update(data)

    # Simpan ke file JSON dengan format yang diinginkan (key: "judul_file.txt" : "url")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=4)