import React from 'react';
import './LoadingPage.css';

const LoadingPage = () => {
  return (
    <div className="loading-container">
      <div className="loading-content">
        <div className="loading-spinner"></div>
        <h2>Creating Your Design</h2>
        <p>Please wait while we process your request...</p>
      </div>
    </div>
  );
};

export default LoadingPage;
