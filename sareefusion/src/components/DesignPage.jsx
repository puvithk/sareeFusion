import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import LoadingPage from './LoadingPage';
import './DesignPage.css';

const DesignPage = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [imagesLoaded, setImagesLoaded] = useState(false);
  const navigate = useNavigate();

  // Sample images - replace with your actual image paths
  const designImages = [
    {
      src: "https://images.unsplash.com/photo-1583394838336-acd977736f90?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=684&q=80",
      title: "Traditional Elegance",
      description: "Classic patterns with modern touches"
    },
    {
      src: "https://images.unsplash.com/photo-1583394838336-acd977736f90?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=684&q=80",
      title: "Contemporary Fusion",
      description: "Modern designs with traditional elements"
    }
  ];

  useEffect(() => {
    // Simulate backend response delay
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 2000);

    return () => clearTimeout(timer);
  }, []);

  const handleImageLoad = () => {
    setImagesLoaded(true);
  };

  if (isLoading) {
    return <LoadingPage />;
  }

  return (
    <div className="design-page">
      <div className="container py-5">
        <h1 className="text-center mb-5" style={{
          color: '#213547',
          fontWeight: 'bold',
          textShadow: '1px 1px 2px rgba(0,0,0,0.1)'
        }}>
          Our Designs
        </h1>
        
        <div className="row justify-content-center g-4">
          {designImages.map((design, index) => (
            <div key={index} className="col-md-6">
              <div className="design-card">
                <div className="image-container">
                  <img 
                    src={design.src}
                    alt={design.title}
                    className="img-fluid rounded"
                    style={{
                      boxShadow: '0 4px 15px rgba(0,0,0,0.1)',
                      transition: 'transform 0.3s ease',
                      opacity: imagesLoaded ? 1 : 0
                    }}
                    onLoad={handleImageLoad}
                  />
                  {!imagesLoaded && (
                    <div className="image-placeholder">
                      <div className="placeholder-spinner"></div>
                    </div>
                  )}
                </div>
                <div className="design-info mt-3">
                  <h3>{design.title}</h3>
                  <p>{design.description}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default DesignPage;
