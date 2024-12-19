import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from pymongo import MongoClient

# Fungsi untuk mengambil artikel dari halaman Motorace dengan BeautifulSoup
def get_motorace_article_links(url, max_links_per_day=10):
    try:
        # Mengirim permintaan HTTP ke URL
        response = requests.get(url)
        response.raise_for_status()  # Cek apakah permintaan berhasil
        
        # Debugging: Periksa apakah halaman berhasil diambil
        print(f"Successfully fetched: {url}")
        
        # Parsing konten HTML dengan BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Menemukan semua link artikel menggunakan selector CSS yang lebih tepat
        article_links = []
        for a_tag in soup.select('a.news-list__link'):
            if len(article_links) >= max_links_per_day:  # Batasan per hari
                break
            link = a_tag['href']
            if link.startswith('http'):
                article_links.append(link)
        
        return article_links
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return []

# Fungsi untuk menyambungkan ke MongoDB
def get_mongo_connection():
    client = MongoClient('mongodb://localhost:27017/')  # Menghubungkan ke server MongoDB lokal
    db = client['crawling']  # Menggunakan database 'crawling'
    return db  # Mengembalikan database untuk digunakan dengan koleksi yang berbeda

# Fungsi untuk crawling halaman indeks Motorace berdasarkan tanggal
def crawl_motorace_articles():
    today = datetime.today()
    one_year_ago = today - timedelta(days=365)

    # Iterasi dari hari ini hingga satu tahun kebelakang
    current_date = today
    all_links = []

    # Batas maksimal link yang diambil
    max_links = 1000
    max_links_per_day = 10  # Tambahkan batasan per hari

    while current_date >= one_year_ago and len(all_links) < max_links:
        # Format URL sesuai dengan tanggal dan section_id
        year = current_date.year
        month = current_date.month
        day = current_date.day

        url = f'https://www.motorplus-online.com/indeks?year={year}&month={month}&day={day}&section_id=621'
        print(f'Fetching articles from: {url}')

        # Ambil artikel dari URL tersebut dengan batasan per hari
        links = get_motorace_article_links(url, max_links_per_day)
        all_links.extend(links)

        # Debugging: Tampilkan tanggal dan jumlah link yang diambil
        print(f"Date: {current_date.strftime('%Y-%m-%d')} - Articles found: {len(links)}")

        # Simpan link ke MongoDB selama crawling berlangsung
        save_links_to_mongo(links)

        # Jika jumlah link yang diambil sudah mencapai batas
        if len(all_links) >= max_links:
            print(f"Reached the maximum limit of {max_links} articles.")
            break

        # Mundur ke hari sebelumnya
        current_date -= timedelta(days=1)

    return all_links[:max_links]  # Membatasi jumlah artikel ke 10

# Fungsi untuk menyimpan link ke dalam MongoDB
def save_links_to_mongo(links):
    db = get_mongo_connection()  # Mendapatkan koneksi ke database MongoDB
    motorrace_collection = db['motorrace']  # Koleksi 'motorrace'
    all_links_collection = db['all_links']  # Koleksi 'all_links'
    
    for link in links:
        article_data = {
            'link': link,
            'date_added': datetime.now()  # Menambahkan tanggal ketika artikel ditambahkan
        }
        
        # Menyimpan ke koleksi 'motorrace'
        motorrace_collection.update_one({'link': link}, {'$set': article_data}, upsert=True)
        
        # Menyimpan ke koleksi 'all_links'
        all_links_collection.update_one({'link': link}, {'$set': article_data}, upsert=True)

# Menjalankan fungsi crawling untuk artikel Motorace dan menyimpan hasilnya
if __name__ == "__main__":
    motorace_articles = crawl_motorace_articles()
    print(f"Total articles found: {len(motorace_articles)}")
    print("Links have been saved to MongoDB in both 'motorrace' and 'all_links' collections.")
