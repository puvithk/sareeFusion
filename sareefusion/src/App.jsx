import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import './App.css'
import Navbar from './components/navBar'
import Homepage from './components/HomePage'
import DesignPage from './components/DesignPage'
// import SareeUploadTemplate from './components/SareeUploadTemplate'

function App() {
  return (
    <Router>
      <div>
        <Navbar />
        <Routes>
          <Route path="/" element={<Homepage />} />
          <Route path="/designs" element={<DesignPage />} />
          {/* Add more routes as needed */}
        </Routes>
      </div>
    </Router>
  )
}

export default App
