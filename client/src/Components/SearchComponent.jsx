import { useState } from "react";
import axios from "axios";
import Layout from "../Components/Layouts/Layout";

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

const SearchComponent = ({ category, heroTitle, heroSubtitle, heroImage, searchPlaceholder }) => {
  const [query, setQuery] = useState("");
  const [resultsCosine, setResultsCosine] = useState([]);
  const [resultsJaccard, setResultsJaccard] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPagesCosine, setTotalPagesCosine] = useState(1);
  const [totalPagesJaccard, setTotalPagesJaccard] = useState(1);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [searchTime, setSearchTime] = useState(null);
  const [error, setError] = useState("");

  const handleSearch = async () => {
    if (!query.trim()) {
      setError("Please enter a search query.");
      return;
    }
    setError("");
    setLoading(true);
    setSearched(true);

    const startTime = new Date();

    try {
      const [cosineResponse, jaccardResponse] = await Promise.all([
        axios.post(`${API_URL}/search`, {
          category,
          scoring: "cosine",
          query,
        }),
        axios.post(`${API_URL}/search`, {
          category,
          scoring: "jaccard",
          query,
        }),
      ]);

      const processResults = (data) =>
        data
          .sort((a, b) => b.score - a.score)
          .map((result) => {
            const scorePercentage = (result.score * 100).toFixed(2);

            const snippetLength = 200;
            let snippet = result.snippet;
            if (snippet.length > snippetLength) {
              const lastSpace = snippet.lastIndexOf(" ", snippetLength);
              snippet = snippet.slice(0, lastSpace) + " ...";
            }

            return {
              ...result,
              score: scorePercentage,
              snippet: snippet,
            };
          });

      const processedCosine = processResults(cosineResponse.data);
      const processedJaccard = processResults(jaccardResponse.data);

      setResultsCosine(processedCosine);
      setResultsJaccard(processedJaccard);

      setTotalPagesCosine(Math.ceil(processedCosine.length / 10));
      setTotalPagesJaccard(Math.ceil(processedJaccard.length / 10));
      setCurrentPage(1);

      const endTime = new Date();
      setSearchTime(((endTime - startTime) / 1000).toFixed(2));
    } catch (error) {
      console.error("Error searching:", error);
    }

    setLoading(false);
    document.getElementById("results")?.scrollIntoView({ behavior: "smooth" });
  };

  const handlePageChange = (page) => {
    setCurrentPage(page);
  };

  const displayResultsCosine = resultsCosine.slice(
    (currentPage - 1) * 10,
    currentPage * 10
  );
  const displayResultsJaccard = resultsJaccard.slice(
    (currentPage - 1) * 10,
    currentPage * 10
  );

  return (
    <Layout>
      <div className="min-h-screen bg-[#0f0606] text-gray-200">
        <div
          className="relative bg-cover bg-center h-screen"
          style={{ backgroundImage: `url('${heroImage}')` }}
        >
          <div
            className="absolute inset-0"
            style={{
              background:
                "linear-gradient(rgba(15, 6, 6, 0.6), rgba(15, 6, 6, 0.9))",
            }}
          ></div>
          <div className="container mx-auto px-6 relative z-6 flex flex-col justify-center h-full">
            <h1 className="text-white text-3xl font-bold">{heroTitle}</h1>
            <p className="text-gray-400 mt-2 text-sm">{heroSubtitle}</p>
            <div className="mt-6 flex flex-wrap gap-4">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="p-3 w-full lg:w-1/3 rounded-lg bg-gray-800 text-white shadow-md border border-gray-600"
                placeholder={searchPlaceholder}
              />

              <button
                onClick={handleSearch}
                className="px-4 py-3 bg-red-600 text-white rounded-lg shadow-lg hover:bg-red-700"
              >
                Search
              </button>
            </div>
            {error && (
              <div className="mt-4 text-red-600 ">
                <p>{error}</p>
              </div>
            )}
          </div>
        </div>

        {!searched && (
          <div className="text-center py-20">
            <h2 className="text-2xl font-bold text-gray-300">
              {`Silakan coba mencari berita ${category} terbaru`}
            </h2>
            <p className="text-gray-400 mt-2">
              {`Masukkan kata kunci pencarian untuk mulai menemukan berita terbaru seputar dunia ${category}.`}
            </p>
          </div>
        )}

        {searched && (
          <div
            id="results"
            className="container-md mx-auto mt-6 flex gap-4 px-6 bg-[#0f0606] rounded-lg"
          >
            <div className="w-full px-6 rounded-lg shadow-xl">
              {loading ? (
                <p className="text-center">Loading...</p>
              ) : (
                <>
                  {searchTime && (
                    <div className="mb-4 text-center text-gray-300">
                      <p>
                        Search completed in {" "}
                        <span className="font-bold">{searchTime} seconds</span>.
                      </p>
                    </div>
                  )}

                  <div className="grid grid-cols-6 gap-6">
                    <div className="col-span-3">
                      <h2 className="text-xl pb-4 font-bold text-white text-center">Cosine</h2>
                      {displayResultsCosine.map((result, index) => (
                        <div
                          key={index}
                          className="bg-[#2f0000] border border-[#450000] p-6 rounded-lg shadow-lg mb-4"
                        >
                          <img
                            src={result.image_url}
                            alt={result.title}
                            className="w-full h-48 object-cover rounded-lg"
                          />
                          <h3 className="text-white font-bold mt-2">{result.title}</h3>
                          <p className="text-sm text-[#D4D4D4] mt-2">
                            Date: {result.date}
                          </p>
                          <p className="text-sm text-[#D4D4D4] mt-1">
                            Score: {result.score}%
                          </p>
                          <p className="text-[#F5F5F5] mt-2">{result.snippet}</p>
                          <a
                            href={result.url}
                            className="text-[#FF6F61] mt-2 inline-block hover:underline"
                            target="_blank"
                            rel="noopener noreferrer"
                          >
                            Read more
                          </a>
                        </div>
                      ))}
                    </div>

                    <div className="col-span-3">
                      <h2 className="text-xl pb-4 font-bold text-white text-center">Jaccard</h2>
                      {displayResultsJaccard.map((result, index) => (
                        <div
                          key={index}
                          className="bg-[#2f0000] border border-[#450000] p-6 rounded-lg shadow-lg mb-4"
                        >
                          <img
                            src={result.image_url}
                            alt={result.title}  
                            className="w-full h-48 object-cover rounded-lg"
                          />
                          <h3 className="text-white font-bold mt-2">{result.title}</h3>
                          <p className="text-sm text-[#D4D4D4] mt-2">
                            Date: {result.date}
                          </p>
                          <p className="text-sm text-[#D4D4D4] mt-1">
                            Score: {result.score}%
                          </p>
                          <p className="text-[#F5F5F5] mt-2">{result.snippet}</p>
                          <a
                            href={result.url}
                            className="text-[#FF6F61] mt-2 inline-block hover:underline"
                            target="_blank"
                            rel="noopener noreferrer"
                          >
                            Read more
                          </a>
                        </div>
                      ))}
                    </div>
                  </div>

                  {resultsCosine.length > 0 || resultsJaccard.length > 0 ? (
                    <div className="mt-6 flex justify-between items-center">
                      <button
                        onClick={() => handlePageChange(currentPage - 1)}
                        disabled={currentPage === 1}
                        className="bg-red-600 px-4 py-2 rounded-lg text-white hover:bg-red-700"
                      >
                        Previous
                      </button>
                      <p className="text-white">
                        Page {currentPage} of {" "}
                        {Math.max(totalPagesCosine, totalPagesJaccard)}
                      </p>
                      <button
                        onClick={() => handlePageChange(currentPage + 1)}
                        disabled={
                          currentPage ===
                          Math.max(totalPagesCosine, totalPagesJaccard)
                        }
                        className="bg-red-600 px-4 py-2 rounded-lg text-white hover:bg-red-700"
                      >
                        Next
                      </button>
                    </div>
                  ) : (
                    <div className="text-center py-20">
                      <h2 className="text-2xl font-bold text-gray-300">
                        Maaf, tidak ada data relevan
                      </h2>
                      <p className="text-gray-400 mt-2">
                        Cobalah kata kunci yang lain untuk mendapatkan hasil
                        pencarian.
                      </p>
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default SearchComponent;
