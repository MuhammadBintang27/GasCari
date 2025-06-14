import { useState, useEffect } from "react";
import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

const useSearch = (query) => {
  const [resultsCosine, setResultsCosine] = useState([]);
  const [resultsJaccard, setResultsJaccard] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [searchTime, setSearchTime] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPagesCosine, setTotalPagesCosine] = useState(1);
  const [totalPagesJaccard, setTotalPagesJaccard] = useState(1);
  const [error, setError] = useState(null);

  const category = "all";

  const handleSearch = async () => {
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

            // Ensuring snippets are not cut off abruptly
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

      // Set total pages based on the results of each algorithm
      setTotalPagesCosine(Math.ceil(processedCosine.length / 6));
      setTotalPagesJaccard(Math.ceil(processedJaccard.length / 6));
      setCurrentPage(1);

      const endTime = new Date();
      setSearchTime(((endTime - startTime) / 1000).toFixed(2));
    } catch (error) {
      console.error("Error searching:", error);
      setError(error.message);
    }

    setLoading(false);
  };

  const handlePageChange = (page) => {
    setCurrentPage(page);
  };

  const displayResultsCosine = resultsCosine.slice(
    (currentPage - 1) * 6,
    currentPage * 6
  );
  const displayResultsJaccard = resultsJaccard.slice(
    (currentPage - 1) * 6,
    currentPage * 6
  );

  // Auto-scroll to results after search
  useEffect(() => {
    if (searched) {
      const resultsElement = document.getElementById("results");
      if (resultsElement) {
        resultsElement.scrollIntoView({ behavior: "smooth" });
      }
    }
  }, [searched]);

  return {
    resultsCosine,
    resultsJaccard,
    loading,
    searched,
    searchTime,
    currentPage,
    totalPagesCosine,
    totalPagesJaccard,
    error,
    handleSearch,
    handlePageChange,
    displayResultsCosine,
    displayResultsJaccard,
  };
};

export default useSearch;
