def extract_snippet(document, query, max_length=200):
    """Menghasilkan snippet dari dokumen berdasarkan query tanpa memotong kata."""
    start_index = document.lower().find(query.lower())
    if start_index == -1:
        start_index = 0
    
    # Tentukan posisi akhir dari snippet
    end_index = start_index + max_length
    
    # Pastikan snippet tidak terpotong di tengah kata
    if end_index < len(document):
        # Cari spasi mundur dari end_index
        last_space = document.rfind(" ", start_index, end_index)
        if last_space != -1:
            end_index = last_space

    snippet = document[start_index:end_index]
    return snippet.strip() + ("..." if len(document) > end_index else "")
