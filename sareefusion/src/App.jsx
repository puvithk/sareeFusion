import React from 'react'
import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import './App.css'
import Navbar from './components/navBar'
import Homepage from './components/HomePage'
import DesignPage from './components/DesignPage'
// import SareeUploadTemplate from './components/SareeUploadTemplate'

function App() {
  const [borderId, setBorderId] = useState(null)
  const [palluId, setPalluId] = useState(null)
  const [bodyId, setBodyId] = useState(null)
  return (
    <Router>
      <div>
        <Navbar />
        <Routes>
        <Route path="/" element={<Homepage setBodyId={setBodyId} setBorderId={setBorderId} setPalluId={setPalluId}/>} />
        <Route path="/designs" element={<DesignPage bodyId={bodyId} palluId={palluId} borderId={borderId}/>} />
          {/* Add more routes as needed */}
        </Routes>
      </div>
    </Router>
  )
}

export default App
