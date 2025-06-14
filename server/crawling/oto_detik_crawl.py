import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup MongoDB connection
client = MongoClient(os.getenv("MONGODB_URI", "mongodb://localhost:27017/"))
db = client['crawling']  # Nama database
otodetik_collection = db['otodetik']  # Nama koleksi otodetik
all_links_collection = db['all_links']  # Nama koleksi all_links

# Set untuk melacak semua link yang sudah dikunjungi
visited_links = set()

# Fungsi untuk mengambil URL artikel dari halaman berdasarkan tanggal
def get_urls(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for invalid responses
        soup = BeautifulSoup(response.text, 'html.parser')
        
        links = set()

        # Mencari semua link yang relevan
        for article in soup.select('a'):
            link = article.get('href')
            if link:
                # Pengecekan kategori berdasarkan substring di link
                if link.startswith("https://oto.detik.com/berita/d-"):
                    category = "berita"
                elif link.startswith("https://oto.detik.com/mobil/d-"):
                    category = "mobil"
                elif link.startswith("https://oto.detik.com/motor/d-"):
                    category = "motor"
                else:
                    continue  # Lewati link yang tidak termasuk kategori yang diinginkan

                # Tambahkan link ke kategori yang sesuai jika belum dikunjungi
                if link not in visited_links:
                    links.add((category, link))  # Menyimpan kategori dan URL
                    visited_links.add(link)
        
        return links

    except requests.RequestException as e:
        print(f"Error saat mengambil URL {url}: {e}")
        return set()

# Fungsi untuk menyimpan URL ke koleksi MongoDB
def save_urls(links, category):
    # Menyimpan ke koleksi 'otodetik'
    for link in links:
        otodetik_collection.update_one(
            {"link": link[1]},  # Cek apakah link sudah ada
            {"$set": {"category": link[0], "link": link[1]}},  # Jika ada, update; jika tidak, insert
            upsert=True  # Upsert memungkinkan insert jika document belum ada
        )
        
    # Menyimpan ke koleksi 'all_links'
    for link in links:
        all_links_collection.update_one(
            {"link": link[1]},  # Cek apakah link sudah ada
            {"$set": {"category": link[0], "link": link[1]}},  # Jika ada, update; jika tidak, insert
            upsert=True  # Upsert memungkinkan insert jika document belum ada
        )

# Fungsi untuk mencetak log
def print_log(date, daily_saved_links):
    print(f"Fetching articles for date: {date.strftime('%d/%m/%Y')}")
    for category, count in daily_saved_links.items():
        print(f"  - {count} link {category} tercrawling.")

if __name__ == '__main__':
    # URL dasar untuk kategori yang dipilih, dengan format tanggal seperti yang Anda inginkan
    base_url = "https://oto.detik.com/indeks?date="  # Menggunakan base URL yang diinginkan

    start_date = datetime.now().date()
    # Set end_date to 1 year ago from today
    end_date = start_date - timedelta(days=365)

    # Batas link untuk setiap kategori
    max_links = {'berita': 1000, 'mobil': 700, 'motor': 700}
    daily_link_limit = 10  # Batas maksimal link per hari
    total_links = {'berita': 0, 'mobil': 0, 'motor': 0}  # Melacak jumlah link per kategori

    current_date = start_date

    # Melakukan iterasi mundur dari start_date ke end_date
    while current_date >= end_date and (
        total_links['berita'] < max_links['berita'] or
        total_links['mobil'] < max_links['mobil'] or
        total_links['motor'] < max_links['motor']
    ):
        daily_saved_links = {'berita': 0, 'mobil': 0, 'motor': 0}  # Reset per hari

        # Format tanggal ke URL sesuai format yang diberikan: dd%2Fmm%2Fyyyy
        formatted_date = current_date.strftime('%d%%2F%m%%2F%Y')
        url = f"{base_url}{formatted_date}"

        links = get_urls(url)
        if links:
            for category, link in links:
                # Menyimpan link sesuai kategori yang diterima
                if total_links[category] < max_links[category] and daily_saved_links[category] < daily_link_limit:
                    save_urls([(category, link)], category)
                    total_links[category] += 1
                    daily_saved_links[category] += 1

        # Mencetak log untuk hari tersebut
        print_log(current_date, daily_saved_links)

        # Mundur ke tanggal sebelumnya
        current_date -= timedelta(days=1)

    # Menampilkan status final setelah crawling selesai
    print("Crawling selesai!")
    print(f"Link yang disimpan per kategori: {total_links}")
