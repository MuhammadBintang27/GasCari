import os
import requests
from bs4 import BeautifulSoup
import re
import json
import concurrent.futures
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from pymongo import MongoClient
from datetime import datetime
from utilitas import update_json
import time

def preprocess_text(text):
    """Membersihkan teks dari spasi berlebih dan karakter yang tidak diinginkan."""
    text = re.sub(r'^AutonetMagz\.com\s*–\s*', '', text)
    return re.sub(r'\s+', ' ', text).strip()

def is_valid_url(url):
    """Memeriksa apakah URL sesuai dengan format yang valid."""
    return url.startswith('http')

def extract_image_url_selenium(url):
    """Mengambil URL gambar menggunakan Selenium untuk AutonetMagz."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Menambahkan opsi headless
    chrome_options.add_argument("--disable-gpu")  # Menonaktifkan GPU untuk menghindari masalah di beberapa sistem
    chrome_options.add_argument("--no-sandbox")  # Agar lebih stabil di beberapa lingkungan

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    # Tunggu beberapa detik agar gambar dimuat
    time.sleep(5)

    # Ambil elemen gambar
    image_element = driver.find_element(By.CSS_SELECTOR, '#page > div.wrap.container.wrapmenu > main > article > div.mdl-card__media.mdl-color-text--grey-50 > a > img')
    image_url = image_element.get_attribute('src')

    driver.quit()
    return image_url

def extract_image_url_beautifulsoup(soup, url):
    """Mengambil URL gambar menggunakan BeautifulSoup untuk situs selain AutonetMagz."""
    if 'oto.detik' in url:
        # Selektor untuk Oto Detik
        image_element = soup.find(class_='detail__media-image')
        if image_element and image_element.img:
            return image_element.img['src']

    return "URL gambar tidak ditemukan"

def extract_content(soup, url):
    """Mengambil tanggal, konten artikel, dan membersihkannya."""
    if 'autonetmagz' in url:
        date_element = soup.select_one('#single-article > div.single-meta.col-sm-10 > time')
        date = date_element.get_text(strip=True) if date_element else "Tanggal tidak ditemukan"
        article_body = soup.find(class_='entry-content')
    elif 'oto.detik' in url:
        date_element = soup.find(class_='detail__date')
        date = date_element.get_text(strip=True) if date_element else "Tanggal tidak ditemukan"
        article_body = soup.find(class_='detail__body-text')
    else:
        return None, None

    if article_body:
        paragraphs = [p.get_text() for p in article_body.find_all('p') if not p.has_attr('class')]
        content = preprocess_text('\n'.join(paragraphs))
    else:
        content = "Konten tidak ditemukan di halaman ini."

    return date, content

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
        date, content = extract_content(soup, url)
        if not content:
            skipped_urls.append(url)
            return

        # Ekstraksi gambar
        if 'autonetmagz' in url:
            image_url = extract_image_url_selenium(url)
        else:
            image_url = extract_image_url_beautifulsoup(soup, url)

        title = soup.title.string.strip('"').replace("\n", " ").replace("\r", "") if soup.title else "no_title"
        cleaned_content = preprocess_text(content)

        # Menyimpan ke database
        article_data = {
            'title': title,
            'date': date,
            'content': cleaned_content,
            'image_url': image_url,
            'url': url,
            'date_added': datetime.utcnow()
        }

        mobil_collection.insert_one(article_data)
        all_collection.insert_one(article_data)

        # Simpan URL ke urldoc
        urldoc[title[:100]] = url

        print(f"Berhasil memproses: {url}")

    except Exception as e:
        print(f"Error processing {url}: {e}")
        skipped_urls.append(url)

# Koneksi MongoDB
client = MongoClient('mongodb://localhost:27017/')
db_crawling = client['crawling']
collection_otodetik = db_crawling['otodetik']
collection_autonetmagz = db_crawling['autonetmagz']

db_scrapping = client['scrapping']
mobil_collection = db_scrapping['mobil']
all_collection = db_scrapping['all']

# Membaca URL dari MongoDB
urls = urls = (
    [doc['link'] for doc in collection_otodetik.find({'category': 'mobil'})] +
    [doc['link'] for doc in collection_autonetmagz.find({'category': 'mobil'})]
)


urldoc = {}
skipped_urls = []

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
}

# Gunakan ThreadPoolExecutor untuk pemrosesan paralel
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    executor.map(process_url, urls)

# Update JSON file
update_json(os.path.join('urldoc', 'mobil_urldoc.json'), urldoc)
update_json(os.path.join('urldoc', 'all_urldoc.json'), urldoc)

# Simpan URL yang gagal diproses
with open('skipped_urls.txt', 'w', encoding='utf-8') as f:
    for url in skipped_urls:
        f.write(url + '\n')

print("Proses selesai.")
