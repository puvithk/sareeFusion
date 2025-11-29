import React from 'react';

const Navbar = () => {
  return (
    <nav className="navbar navbar-expand-lg fixed-top" style={{
      background: 'linear-gradient(135deg, #6a11cb 0%, #2575fc 100%)',
      boxShadow: '0 2px 10px rgba(0,0,0,0.1)'
    }}>
      <div className="container">
        <a className="navbar-brand" href="#" style={{
          color: '#ffffff',
          fontSize: '1.5rem',
          fontWeight: 'bold',
          textShadow: '1px 1px 2px rgba(0,0,0,0.2)'
        }}>
          SareeFusion
        </a>
        <button 
          className="navbar-toggler" 
          type="button" 
          data-bs-toggle="collapse" 
          data-bs-target="#navbarNav"
          style={{ border: '1px solid rgba(255,255,255,0.5)' }}
        >
          <span className="navbar-toggler-icon"></span>
        </button>
        <div className="collapse navbar-collapse" id="navbarNav">
          <ul className="navbar-nav ms-auto">
            <li className="nav-item">
              <a className="nav-link" href="#" style={{
                color: '#ffffff',
                fontSize: '1.1rem',
                padding: '0.5rem 1rem',
                margin: '0 0.2rem',
                borderRadius: '5px',
                transition: 'all 0.3s ease'
              }} onMouseOver={(e) => e.target.style.backgroundColor = 'rgba(255,255,255,0.1)'}
                onMouseOut={(e) => e.target.style.backgroundColor = 'transparent'}>
                Home
              </a>
            </li>
            <li className="nav-item">
              <a className="nav-link" href="#" style={{
                color: '#ffffff',
                fontSize: '1.1rem',
                padding: '0.5rem 1rem',
                margin: '0 0.2rem',
                borderRadius: '5px',
                transition: 'all 0.3s ease'
              }} onMouseOver={(e) => e.target.style.backgroundColor = 'rgba(255,255,255,0.1)'}
                onMouseOut={(e) => e.target.style.backgroundColor = 'transparent'}>
                Gallery
              </a>
            </li>
            <li className="nav-item">
              <a className="nav-link" href="#" style={{
                color: '#ffffff',
                fontSize: '1.1rem',
                padding: '0.5rem 1rem',
                margin: '0 0.2rem',
                borderRadius: '5px',
                transition: 'all 0.3s ease'
              }} onMouseOver={(e) => e.target.style.backgroundColor = 'rgba(255,255,255,0.1)'}
                onMouseOut={(e) => e.target.style.backgroundColor = 'transparent'}>
                About
              </a>
            </li>
            <li className="nav-item">
              <a className="nav-link" href="#" style={{
                color: '#ffffff',
                fontSize: '1.1rem',
                padding: '0.5rem 1rem',
                margin: '0 0.2rem',
                borderRadius: '5px',
                transition: 'all 0.3s ease'
              }} onMouseOver={(e) => e.target.style.backgroundColor = 'rgba(255,255,255,0.1)'}
                onMouseOut={(e) => e.target.style.backgroundColor = 'transparent'}>
                Contact
              </a>
            </li>
          </ul>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;