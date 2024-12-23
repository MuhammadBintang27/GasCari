import React from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";

import ScrollToTop from "./Components/Elements/ScrollToTop";

import Mobil from "./Pages/Mobil";
import Motor from "./Pages/Motor";
import MotorRace from "./Pages/MotorRace";
import Berita from "./Pages/Berita";
import All from "./Pages/All";  
const App = () => {
  return (
    <Router>
      <ScrollToTop />
      <Routes>
        <Route path="/mobil" element={<Mobil />} />
        <Route path="/motor" element={<Motor />} />
        <Route path="/motor-race" element={<MotorRace />} />
        <Route path="/berita" element={<Berita />} />
        <Route path="/all" element={<All />} />
        {/* Default route */}
        <Route path="/" element={<All />} />
      </Routes>
    </Router>
  );
};

export default App;
