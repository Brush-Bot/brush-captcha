import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import Login from "./pages/Login";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import "antd/dist/reset.css";

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <BrowserRouter>
    <Routes>
      <Route path="/login" element={<Login onLogin={() => window.location.href = "/"} />} />
      <Route path="/*" element={<App />} />
    </Routes>
  </BrowserRouter>
);
