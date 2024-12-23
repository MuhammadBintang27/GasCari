import React, { useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";

const Nav = () => {
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const navigate = useNavigate();
  const location = useLocation(); // Mengambil lokasi saat ini

  const toggleSearch = () => {
    setIsSearchOpen(!isSearchOpen);
    setSearchQuery(""); // Reset input ketika toggling
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?query=${encodeURIComponent(searchQuery)}`);
      setIsSearchOpen(false); // Tutup setelah mencari
    }
  };

  // Fungsi untuk memeriksa apakah route saat ini sama dengan route yang diberikan
  const isActive = (route) => location.pathname === `/${route}`;
  const routeNames = {
    berita: 'News',
    'motor-race': 'Motor Race',
    mobil: 'Cars',
    motor: 'Motorcycles',
    all: 'All',
  };
  return (
    <div className="fixed top-0 left-0 w-full p-4 z-10">
      <div className="container mx-auto flex justify-between items-center">
        {/* Logo */}
        <div className="text-white text-2xl font-bold">GasCari</div>

        {/* Navigation Links */}
        <div className="flex gap-10 text-white">
          {['berita', 'motor-race', 'mobil', 'motor', 'all'].map((route) => (
            <Link
              key={route}
              to={`/${route}`}
              className={`group hover:text-gray-400 transition-all duration-300 ease-in-out transform hover:scale-105 ${
                isActive(route) ? "border-b-2 border-white" : ""
              }`} // Menambahkan garis bawah jika route aktif
            >
              <span className="group-hover:text-gray-400">
                {routeNames[route] || route.charAt(0).toUpperCase() + route.slice(1)} {/* Display English name */}
              </span>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Nav;
