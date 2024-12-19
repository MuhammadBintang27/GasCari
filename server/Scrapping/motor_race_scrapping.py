import os
import requests
from bs4 import BeautifulSoup
import re
import pymongo
from datetime import datetime
import json
from utilitas import update_json

# Menghubungkan ke MongoDB
client = pymongo.MongoClient('mongodb://localhost:27017')  # Ganti dengan URL MongoDB jika berbeda
db = client['crawling']  # Database crawling
motorrace_collection = db['motorrace']  # Koleksi motorrace yang menyimpan URL

scrapping_db = client['scrapping']  # Database scrapping
scrapping_collection = scrapping_db['motorrace']  # Koleksi motorrace untuk menyimpan artikel
all_collection = scrapping_db['all']  # Koleksi "all" untuk menyimpan semua artikel dari berbagai kategori

urldoc_directory = 'urldoc'  # Ganti dengan path direktori tempat menyimpan urldoc.json

def preprocess_text(text):
    """Membersihkan teks dari spasi berlebih dan karakter yang tidak diinginkan"""
    text = re.sub(r'MOTOR\s*Plus\s*[-\w]*\s*[-:]*online\.com\s*[-:]*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'MOTOR\s*Plus[-\w]*\.com\s*[-:]*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def clean_filename(title):
    """Membersihkan judul dari karakter yang tidak valid untuk dijadikan nama file dan menghapus ' - Motorplus'"""
    title = title.replace(" - Motorplus", "")
    return "".join(c for c in title if c.isalnum() or c.isspace()).strip()

def improve_title(title):
    """Memperbaiki judul artikel agar lebih menarik dan profesional"""
    # Menghapus '- Motorplus' atau '- motorplus' dari judul
    title = title.replace(" - Motorplus", "").replace(" - motorplus", "")
    
    # Menambahkan spasi di antara huruf besar yang terhubung
    title = re.sub(r'([a-z])([A-Z])', r'\1 \2', title)
    
    # Memperbaiki kapitalisasi judul menjadi lebih rapi
    title = title.strip()  # Menghapus spasi di awal dan akhir
    title = title.title()  # Mengubah setiap kata untuk dimulai dengan huruf kapital
    
    return title

def read_urls_from_mongo():
    """Membaca URL dari MongoDB dan mengembalikan sebagai list"""
    urls = []
    cursor = motorrace_collection.find()  # Mengambil semua dokumen dalam koleksi 'motorrace'
    for doc in cursor:
        urls.append(doc['link'])  # Mengambil 'link' dari setiap dokumen dan menambahkannya ke list
    return urls  # Mengembalikan daftar URL

def is_valid_url(url):
    """Memeriksa apakah URL sesuai dengan format yang valid"""
    return url.startswith('http')

def save_to_mongo(category, data):
    """
    Menyimpan data ke dalam koleksi MongoDB berdasarkan kategori yang diberikan.
    Data juga akan disimpan ke dalam koleksi `all`.
    """
    category_collection = scrapping_db[category]

    for filename, article_data in data.items():
        # Simpan ke koleksi kategori
        category_collection.update_one(
            {"title": filename},  # Menentukan filter untuk data yang sudah ada
            {"$set": article_data},  # Mengupdate atau menyimpan artikel baru
            upsert=True  # Jika tidak ada, maka data akan dimasukkan
        )
        
        # Simpan ke koleksi all
        all_collection.update_one(
            {"title": filename},
            {"$set": article_data},
            upsert=True
        )

# Membaca URL dari MongoDB
urls = read_urls_from_mongo()

# Menyimpan artikel per kategori
skipped_urls = []
urldoc = {}

# Header HTTP untuk permintaan
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
}

for url in urls:
    try:
        # Periksa validitas URL
        if not is_valid_url(url):
            skipped_urls.append(url)
            print(f"URL tidak valid: {url}")
            continue
        
        # Permintaan GET untuk mengambil halaman
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # Pastikan encoding yang benar untuk decoding karakter
        response.encoding = response.apparent_encoding

        # Membuat objek BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Ambil tanggal dari elemen dengan class read__time
        date_element = soup.select_one('.read__time')
        date = date_element.get_text(strip=True) if date_element else "Tanggal tidak ditemukan"

        # Ambil konten dari elemen dengan class read__right
        article_body = soup.find(class_='read__right')
        if article_body:
            paragraphs = [p.get_text() for p in article_body.find_all('p')]
            content = '\n'.join(paragraphs)
        else:
            content = "Konten tidak ditemukan di halaman ini."
        
        # Preprocess text (membersihkan teks)
        cleaned_content = preprocess_text(content)

        # Ambil judul artikel
        title = soup.title.string if soup.title else "no_title"
        title = improve_title(title)  # Memperbaiki judul

        # Bersihkan judul untuk menjadi nama file yang valid
        filename = clean_filename(title)

        # Ambil link gambar dari elemen dengan class "photo__item"
        image_element = soup.select_one('.photo__item img')
        if image_element:
            image_url = image_element.get('src') or image_element.get('data-src')
        else:
            image_url = None

        # Log hasil ekstraksi
        print(f"URL: {url}")
        print(f"Title: {title}")
        print(f"Tanggal: {date}")
        print(f"Konten (preview): {content[:200]}...")  # Menampilkan preview 200 karakter dari konten
        if image_url:
            print(f"URL Gambar: {image_url}")
        else:
            print("Gambar tidak ditemukan")

        # Menyusun data artikel
        article_data = {
            'title': title,
            'date': date,
            'content': cleaned_content,
            'image_url': image_url,
            'url': url,
            'date_added': datetime.utcnow()  # Menyimpan tanggal saat artikel ditambahkan
        }

        # Simpan ke MongoDB menggunakan fungsi save_to_mongo
        save_to_mongo("motorrace", {filename: article_data})

    except Exception as e:
        print(f"Error processing {url}: {str(e)}")
        skipped_urls.append(url)

# Membaca urldoc yang sudah ada dari file JSON jika ada
update_json(os.path.join(urldoc_directory, 'berita_urldoc.json'), urldoc)
update_json(os.path.join(urldoc_directory, 'all_urldoc.json'), urldoc)

# Menyimpan daftar URL yang gagal diproses
with open('skipped_urls.txt', 'w') as f:
    for url in skipped_urls:
        f.write(url + '\n')

print("Proses selesai.")
