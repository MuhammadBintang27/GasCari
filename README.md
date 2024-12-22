
# GasCari: Automotive Information Retrieval System

## Table of Contents

1. [Introduction](#introduction)
2. [Features](#features)
3. [Technologies Used](#technologies-used)
4. [Setup Instructions](#setup-instructions)
5. [Usage](#usage)
6. [Contributing](#contributing)


---

## Introduction

Selamat datang di proyek **GasCari**! Proyek ini bertujuan untuk mengembangkan sistem penelusuran informasi yang canggih dan efisien di sektor otomotif. Sistem ini memungkinkan pengguna untuk menemukan artikel otomotif yang relevan dari berbagai sumber berita terkemuka, seperti **Autonetmagz**, **Motorplus**, dan **Oto-Detik**.

Dengan memanfaatkan metode pembobotan seperti **Cosine Similarity** dan **Jaccard Similarity**, sistem ini akan membandingkan query pengguna dengan artikel yang ada untuk menentukan artikel mana yang paling relevan. Proyek ini dibuat sebagai tugas final mata kuliah *Penelusuran Informasi*, sekaligus untuk mengatasi tantangan dalam mengembangkan sistem pencarian informasi yang cerdas di dunia otomotif.

---

## Features

- **Crawling**: Mengumpulkan URL artikel dari berbagai situs otomotif terkemuka.
- **Scraping**: Mengakses dan mengekstrak konten artikel secara langsung dari halaman web.
- **Data Preprocessing**: Pembersihan teks, penghilangan stopwords, dan penerapan stemming untuk mempersiapkan data.
- **TF-IDF**: Penggunaan teknik Term Frequency-Inverse Document Frequency (TF-IDF) untuk memberikan pembobotan pada kata-kata dalam artikel.
- **Similarity Calculations**: Menggunakan **Cosine Similarity** dan **Jaccard Similarity** untuk menghitung kesamaan antara query pencarian dan artikel.
- **Responsive User Interface**: Antarmuka pengguna yang dinamis menggunakan **React** dan **Tailwind CSS**, memungkinkan pengalaman yang interaktif dan mudah digunakan.
- **Kategori Artikel**: Tersedia lima kategori artikel: **All**, **Motor**, **Mobil**, **MotorRace**, dan **Berita**. Pengguna dapat memilih kategori yang relevan untuk mencari artikel sesuai minat.

---

## Technologies Used

- **React**: Untuk membangun antarmuka pengguna yang dinamis dan responsif.
- **Tailwind CSS**: Framework CSS untuk desain yang cepat dan fleksibel.
- **Flask**: Backend framework untuk menangani permintaan dan pengolahan data.
- **Selenium** & **BeautifulSoup**: Untuk scraping dan ekstraksi data dari web.
- **Scikit-learn**: Digunakan untuk menghitung similarity dan analisis teks.
- **Sastrawi** & **NLTK**: Digunakan untuk proses stemming dan pemrosesan bahasa alami.
- **MongoDB**: Penyimpanan data berbasis NoSQL untuk artikel dan informasi terkait.

---

## Setup Instructions

Ikuti langkah-langkah berikut untuk menjalankan aplikasi di mesin Anda:

1. **Clone Repository**:
   ```bash
   git clone [repository-url]
   ```

2. **Masuk ke Direktori Proyek**:
   ```bash
   cd [project-directory]
   ```

3. **Instalasi Dependensi Client**:
   - Buka terminal untuk bagian client dan arahkan ke folder client.
   - Instal dependensi dengan perintah:
     ```bash
     npm install
     ```

4. **Instalasi Dependensi Server**:
   - Buka terminal kedua untuk bagian server dan arahkan ke folder server.
   - Instal dependensi Python dengan perintah:
     ```bash
     pip install -r requirements.txt
     ```

5. **Menjalankan Aplikasi**:
   - Untuk menjalankan bagian client:
     ```bash
     npm run dev
     ```
   - Untuk menjalankan bagian server:
     ```bash
     python scoring/app.py
     ```

---

## Usage

Setelah aplikasi berjalan, berikut adalah cara menggunakannya:

1. Pilih kategori artikel di navbar: **All**, **Motor**, **Mobil**, **MotorRace**, atau **Berita**.
2. Masukkan kata kunci atau kalimat dalam kolom pencarian.
3. Sistem akan menampilkan artikel-artikel yang relevan berdasarkan kategori yang dipilih, menggunakan metode pembobotan **Cosine Similarity** dan **Jaccard Similarity** untuk menentukan relevansi.
4. Bandingkan hasil pencarian dan pilih artikel yang paling sesuai dengan kebutuhan Anda.

---

## Contributing

We welcome contributions from everyone! If you want to contribute, follow these steps:

1. Fork the repository
2. Create a feature branch:
   ```bash
   git checkout -b feature/[feature-name]
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add [feature-name]"
   ```
4. Push the changes to your branch:
   ```bash
   git push origin feature/[feature-name]
   ```
5. Create a pull request

---


