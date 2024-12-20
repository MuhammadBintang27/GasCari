import os
import re
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

# Inisialisasi StopWordRemoverFactory
stop_factory = StopWordRemoverFactory()

# Fungsi untuk membaca stopwords dari file dengan jalur relatif
def load_additional_stopwords(file_name):
    # Mendapatkan direktori skrip yang sedang dijalankan
    dir_path = os.path.dirname(os.path.realpath(__file__))
    # Membentuk jalur relatif ke file stopword.txt
    file_path = os.path.join(dir_path, file_name)
    
    with open(file_path, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file.readlines()]

# Memuat stopwords tambahan dari file stopword.txt
additional_stopwords = load_additional_stopwords('stopword.txt')

# Gabungkan stopwords bawaan dengan tambahan
custom_stopwords = stop_factory.get_stop_words() + additional_stopwords

# Buat class custom untuk menghapus stopwords berdasarkan daftar yang diperbarui
class CustomStopWordRemover:
    def __init__(self, stop_words):
        self.stop_words = set(stop_words)

    def remove(self, text):
        # Tokenisasi dengan memperhatikan tanda baca
        words = re.findall(r'\b\w+\b', text)  # Menggunakan regex untuk menangkap kata yang lebih baik
        filtered_words = [word for word in words if word not in self.stop_words]
        return ' '.join(filtered_words)

# Inisialisasi custom stopword remover
custom_stopword_remover = CustomStopWordRemover(custom_stopwords)

# Inisialisasi stemmer Sastrawi
stemmer_factory = StemmerFactory()
stemmer = stemmer_factory.create_stemmer()

# Fungsi untuk membersihkan query
def clean_query(query):
    # Mengubah teks menjadi huruf kecil dan menghapus tanda baca
    query = query.lower()  # Semua menjadi huruf kecil
    query = re.sub(r'[^\w\s]', '', query)  # Menghapus tanda baca
    
    # Hilangkan stopwords
    query_no_stopwords = custom_stopword_remover.remove(query)
    
    # Lakukan stemming
    cleaned_query = stemmer.stem(query_no_stopwords)
    
    return cleaned_query


