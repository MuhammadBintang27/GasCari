import os
import requests
from bs4 import BeautifulSoup
import re
import json
from pymongo import MongoClient
from utilitas import update_json
from datetime import datetime



# Membuat koneksi ke MongoDB
client = MongoClient("mongodb://localhost:27017/")  # Gantilah URL jika menggunakan server MongoDB remote
db_scrapping = client["scrapping"]  # Database scrapping untuk menyimpan hasil scraping
db_crawling = client["crawling"]  # Database crawling untuk mengambil URL
otodetik_collection = db_crawling["otodetik"]  # Koleksi otodetik dalam database crawling

def preprocess_text(text):
    """Membersihkan teks dari spasi berlebih dan karakter yang tidak diinginkan."""
    return re.sub(r'\s+', ' ', text).strip()

def is_valid_url(url):
    """Memeriksa apakah URL sesuai dengan format yang valid."""
    return url.startswith('http')

def extract_image_url_oto_detik(soup):
    """Mengambil URL gambar dari oto.detik."""
    image_element = soup.find(class_='detail__media-image')
    if image_element and image_element.img:
        return image_element.img['src']
    return "URL gambar tidak ditemukan"  # Mengembalikan pesan jika gambar tidak ditemukan

def extract_content_oto_detik(soup):
    """Mengambil tanggal, konten artikel, dan membersihkannya dari oto.detik."""
    date_element = soup.find(class_='detail__date')
    date = date_element.get_text(strip=True) if date_element else "Tanggal tidak ditemukan"
    
    article_body = soup.find(class_='detail__body-text')
    
    if article_body:
        # Hanya mengambil paragraf yang tidak memiliki atribut 'class'
        paragraphs = [p.get_text() for p in article_body.find_all('p') if not p.has_attr('class')]
        content = preprocess_text('\n'.join(paragraphs)) if paragraphs else "Tidak ada konten yang sesuai."
    else:
        content = "Konten tidak ditemukan di halaman ini."

    return date, content

def save_to_mongo(category, data):
    """
    Menyimpan data ke dalam koleksi MongoDB berdasarkan kategori yang diberikan.
    Data juga akan disimpan ke dalam koleksi `all`.
    Format data yang diterima adalah { "title": "url", "content": "konten artikel", "image_url": "url gambar", "date": "tanggal" }
    """
    # Koleksi berdasarkan kategori
    category_collection = db_scrapping[category]
    
    # Koleksi umum (all)
    all_collection = db_scrapping["all"]
    
    # Menambahkan atau memperbarui data di kedua koleksi
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

def process_url(url):
    """Memproses URL untuk ekstraksi data dan penyimpanan konten."""
    try:
        if not is_valid_url(url):
            skipped_urls.append(url)
            print(f"URL tidak valid: {url}")
            return

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, 'html.parser')

        # Ekstraksi data
        date, content = extract_content_oto_detik(soup)
        if not content:
            skipped_urls.append(url)
            return

        # Ekstraksi gambar
        image_url = extract_image_url_oto_detik(soup)

        title = soup.title.string.strip('"').replace("\n", " ").replace("\r", "") if soup.title else "no_title"
        short_title = title[:100]
        filename = "".join(c for c in short_title if c.isalnum() or c.isspace()).rstrip()  # Tidak ada .txt di belakang

        # Membuat data yang akan disimpan ke MongoDB
        article_data = {
            'title': title,
            'date': date,
            'content': content,
            'image_url': image_url,
            'url': url,
            'date_added': datetime.utcnow()
        }

        # Menyimpan data ke MongoDB
        save_to_mongo("berita", {filename: article_data})

        # Menyimpan URL ke JSON dalam format yang diinginkan
        urldoc[filename] = url  # Format key = filename, value = url

        print(f"Berhasil memproses: {url}")

    except Exception as e:
        print(f"Error processing {url}: {e}")
        skipped_urls.append(url)

# Mendapatkan URL dari MongoDB yang memiliki kategori 'berita'
def get_urls_from_mongo():
    """Mengambil semua URL dengan kategori 'berita' dari koleksi crawling di MongoDB."""
    cursor = otodetik_collection.find({"category": "berita"})
    return [doc['link'] for doc in cursor]

# Direktori utama dan file input
urldoc_directory = "urldoc"


# Membuat direktori jika belum ada
os.makedirs(urldoc_directory, exist_ok=True)

# Mendapatkan URL dari MongoDB
urls = get_urls_from_mongo()
urldoc = {}
skipped_urls = []

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
}

# Proses URL untuk oto.detik saja
for url in urls:
    if 'oto.detik' in url:
        process_url(url)

# Update JSON file (optional)
update_json(os.path.join(urldoc_directory, 'berita_urldoc.json'), urldoc)
update_json(os.path.join(urldoc_directory, 'all_urldoc.json'), urldoc)

# Simpan URL yang gagal diproses
with open('skipped_urls.txt', 'w', encoding='utf-8') as f:
    for url in skipped_urls:
        f.write(url + '\n')

print("Proses selesai.")
