import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# def calculate_cosine_similarity(query, documents):
#     """Menghitung Cosine Similarity antara query dan dokumen."""
#     vectorizer = TfidfVectorizer()
#     tfidf_matrix = vectorizer.fit_transform(documents)
#     query_tfidf = vectorizer.transform([query])
#     return cosine_similarity(query_tfidf, tfidf_matrix).flatten()

def calculate_cosine_similarity(query, documents):
    """Menghitung Cosine Similarity antara query dan dokumen."""
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents +[query])
    return cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1]).flatten()

def calculate_jaccard_similarity(query, documents):
    """Menghitung Jaccard Similarity antara query dan dokumen."""
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents)
    query_tfidf = vectorizer.transform([query])

    binary_matrix = (tfidf_matrix > 0).astype(int)
    query_binary = (query_tfidf > 0).astype(int)

    scores = []
    for i in range(binary_matrix.shape[0]):
        intersection = np.logical_and(query_binary.toarray(), binary_matrix[i].toarray()).sum()
        union = np.logical_or(query_binary.toarray(), binary_matrix[i].toarray()).sum()
        scores.append(intersection / union if union != 0 else 0)
    return scores
