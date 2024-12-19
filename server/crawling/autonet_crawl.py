import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin
from pymongo import MongoClient

# Setup MongoDB connection
client = MongoClient("mongodb://localhost:27017/")  # Gantilah dengan URL MongoDB Anda
db = client['crawling']  # Nama database
autonetmagz_collection = db['autonetmagz']  # Koleksi untuk autonetmagz
all_links_collection = db['all_links']  # Koleksi untuk semua link

# Fungsi untuk mengambil artikel dari halaman
def get_autonetmagz_article_links(url, category, max_per_page):
    try:
        # Mengirim permintaan HTTP ke URL
        response = requests.get(url)
        response.raise_for_status()  # Memastikan permintaan berhasil (status code 200)

        # Mengurai HTML dengan BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Menemukan semua link artikel (asumsi link artikel berada di dalam tag <h3><a>)
        article_links = set()  # Menggunakan set untuk memastikan link unik
        for h3_tag in soup.select('h3 > a'):
            if len(article_links) >= max_per_page:
                break  # Batasi hanya 10 link per halaman
            link = h3_tag['href']
            # Menggabungkan dengan base URL jika link relatif
            complete_link = urljoin('https://autonetmagz.com', link)
            article_links.add(complete_link)

        # Jika artikel ditemukan, simpan link ke MongoDB
        if article_links:
            for link in article_links:
                # Menyimpan setiap link ke koleksi autonetmagz
                autonetmagz_collection.update_one(
                    {"link": link},  # Cek apakah link sudah ada
                    {"$set": {"category": category, "link": link}},  # Jika ada, update; jika tidak, insert
                    upsert=True  # Upsert memungkinkan insert jika document belum ada
                )

                # Menyimpan setiap link ke koleksi all_links
                all_links_collection.update_one(
                    {"link": link},  # Cek apakah link sudah ada
                    {"$set": {"link": link}},  # Insert atau update hanya link
                    upsert=True  # Upsert memungkinkan insert jika document belum ada
                )

            print(f"Saved {len(article_links)} links to MongoDB for category '{category}'")
            return len(article_links)  # Mengembalikan jumlah link yang disimpan
        else:
            print(f"No article links found on {url}")
            return 0  # Jika tidak ada link, kembalikan 0

    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return 0  # Jika ada kesalahan, kembalikan 0

# Fungsi untuk menavigasi halaman dan mengambil link dari setiap halaman
def crawl_autonetmagz_pages():
    # Base URL untuk kategori motor dan mobil
    motor_base_url = 'https://autonetmagz.com/category/merek-motor/page/{}/'
    mobil_base_url = 'https://autonetmagz.com/category/merek-mobil/page/{}/'

    # Crawling untuk motor dan mobil secara bergantian
    page_num = 1
    motor_links_saved = 0  # Counter untuk jumlah link yang disimpan
    mobil_links_saved = 0  # Counter untuk jumlah link yang disimpan

    max_total_links = 300  # Maksimal total link per kategori
    max_per_page = 10       # Maksimal link per halaman

    while motor_links_saved < max_total_links or mobil_links_saved < max_total_links:
        if motor_links_saved < max_total_links:
            # Crawling halaman untuk motor
            motor_url = motor_base_url.format(page_num)
            print(f"Fetching motor articles from: {motor_url}")
            motor_links = get_autonetmagz_article_links(motor_url, 'motor', max_per_page)
            motor_links_saved += motor_links  # Menambahkan jumlah link yang disimpan

        if mobil_links_saved < max_total_links:
            # Crawling halaman untuk mobil
            mobil_url = mobil_base_url.format(page_num)
            print(f"Fetching mobil articles from: {mobil_url}")
            mobil_links = get_autonetmagz_article_links(mobil_url, 'mobil', max_per_page)
            mobil_links_saved += mobil_links  # Menambahkan jumlah link yang disimpan

        # Naik ke halaman berikutnya untuk motor dan mobil
        page_num += 1

        # Hentikan jika tidak ada artikel baru pada halaman saat ini
        if motor_links == 0 and mobil_links == 0:
            break

    print(f"Total motor links saved: {motor_links_saved}")
    print(f"Total mobil links saved: {mobil_links_saved}")

# Menjalankan Crawling
if __name__ == '__main__':
    crawl_autonetmagz_pages()
