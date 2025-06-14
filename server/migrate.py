from pymongo import MongoClient

# Koneksi ke MongoDB lokal
local_uri = "mongodb://localhost:27017/Gascari"
local_client = MongoClient(local_uri)

# Koneksi ke MongoDB Atlas
atlas_uri = "mongodb+srv://bintang:tes@designaya.psydxrh.mongodb.net/gascari"
atlas_client = MongoClient(atlas_uri)

# Struktur database dan koleksi yang ingin dipindahkan
db_collections = {
    "crawling": ["all_links", "autonetmagz", "motorrace", "otodetik"],
    "scrapping": ["all", "berita", "mobil", "motor", "motorrace"],
    "processed": ["all", "berita", "mobil", "motor", "motorrace"]
}

for db_name, collections in db_collections.items():
    print(f"\nMigrasi database: {db_name}")
    local_db = local_client[db_name]
    atlas_db = atlas_client[db_name]
    for col in collections:
        print(f"  Migrasi koleksi: {col} ...", end="")
        local_col = local_db[col]
        atlas_col = atlas_db[col]
        docs = list(local_col.find())
        if docs:
            # Hapus _id agar tidak bentrok di Atlas
            for doc in docs:
                doc.pop('_id', None)
            atlas_col.insert_many(docs)
            print(f" {len(docs)} dokumen dipindahkan.")
        else:
            print(" (tidak ada data)")

print("\nMigrasi selesai! Semua data sudah dipindahkan ke MongoDB Atlas.")