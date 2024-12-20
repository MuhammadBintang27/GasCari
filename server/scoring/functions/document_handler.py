import os
import json

def read_documents(folder):
    """Membaca dokumen dari folder output dan mengembalikan daftar konten dan judul."""
    documents = []
    titles = []
    for filename in os.listdir(folder):
        if filename.endswith(".txt"):
            titles.append(os.path.splitext(filename)[0])
            with open(os.path.join(folder, filename), 'r', encoding='utf-8') as file:
                documents.append(file.read())
    return documents, titles

def read_input_documents(folder, url_file):
    """Membaca dokumen dari folder input dan JSON URL, lalu mengembalikan informasi lengkap."""
    documents = []
    titles = []
    details = []

    # Membaca URL dari file JSON
    with open(url_file, 'r', encoding='utf-8') as url_fp:
        url_mapping = json.load(url_fp)

    for filename in os.listdir(folder):
        if filename.endswith(".txt"):
            title = os.path.splitext(filename)[0]
            filepath = os.path.join(folder, filename)
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()

            # Ekstraksi metadata dari file
            lines = content.splitlines()
            tanggalberita = lines[0].replace("Tanggal Berita: ", "").strip() if lines else ""
            img_url = lines[1].replace("URL Gambar: ", "").strip() if len(lines) > 1 else ""
            snippet_start = 2  # Asumsikan snippet dimulai dari baris ke-3
            snippet = " ".join(lines[snippet_start:]).strip()[:200] + ("..." if len(content) > 200 else "")

            # Simpan hasil
            documents.append({
                "title": title,
                "tanggalberita": tanggalberita,
                "img_url": img_url,
                "snippet": snippet,
                "url": url_mapping.get(f"{title}.txt", "")
            })
            titles.append(title)
    return documents, titles
