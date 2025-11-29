//DesignPage.jsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Download, Share2, Heart, Eye, Sparkles } from 'lucide-react';
import LoadingPage from './LoadingPage';
import axios from 'axios';
const NewDesignBanner = ({ design }) => {
  if (!design) return null;

  return (
    <div className="row mb-5">
      <div className="col-12">
        <div 
          className="card border-0 shadow-lg"
          style={{
            borderRadius: '20px',
            background: 'linear-gradient(135deg, #6f42c1 0%, #0d6efd 100%)',
            color: 'white',
            overflow: 'hidden'
          }}
        >
          <div className="card-body p-0">
            <div className="row g-0">
              <div className="col-md-8">
                <div className="p-5">
                  <div className="d-flex align-items-center mb-3">
                    <Sparkles size={24} className="me-2" />
                    <span className="badge bg-light text-primary px-3 py-2">Just Generated!</span>
                  </div>
                  <h2 className="display-5 fw-bold mb-3">Your New Design</h2>
                  <p className="lead mb-4 opacity-90">
                    {design.description || "AI-generated saree design based on your preferences"}
                  </p>
                  <div className="d-flex gap-3 flex-wrap">
                    <button 
                      className="btn btn-light btn-lg d-flex align-items-center gap-2"
                      style={{ borderRadius: '12px' }}
                    >
                      <Download size={20} />
                      Download HD
                    </button>
                    <button 
                      className="btn btn-outline-light btn-lg d-flex align-items-center gap-2"
                      style={{ borderRadius: '12px' }}
                    >
                      <Share2 size={20} />
                      Share Design
                    </button>
                    <button 
                      className="btn btn-outline-light btn-lg d-flex align-items-center gap-2"
                      style={{ borderRadius: '12px' }}
                    >
                      <Heart size={20} />
                      Save to Favorites
                    </button>
                  </div>
                </div>
              </div>
              <div className="col-md-4">
                <div className="h-100 position-relative" style={{ minHeight: '300px' }}>
                  <img 
                    src={design.src}
                    alt={design.title || "Generated Design"}
                    className="w-100 h-100"
                    style={{ 
                      objectFit: 'cover',
                      borderRadius: '0 20px 20px 0'
                    }}
                  />
                  <div className="position-absolute top-0 end-0 m-3">
                    <span className="badge bg-success px-3 py-2">
                      <Sparkles size={14} className="me-1" />
                      New
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const DesignCard = ({ design, index, onImageLoad, isNewlyGenerated }) => {
  const [isLiked, setIsLiked] = useState(false);
  const [imageLoaded, setImageLoaded] = useState(false);

  const handleImageLoad = () => {
    setImageLoaded(true);
    onImageLoad();
  };

  return (
    <div className="col-12 col-md-6 col-lg-4">
      {console.log(design)}
      <div 
        className="card h-100 shadow-sm"
        style={{
          borderRadius: '16px',
          overflow: 'hidden',
          border: 'none',
          background: 'linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%)',
          transition: 'all 0.3s ease'
        }}
        onMouseOver={(e) => e.currentTarget.style.transform = 'translateY(-8px)'}
        onMouseOut={(e) => e.currentTarget.style.transform = 'translateY(0)'}
      >
        <div className="position-relative" style={{ height: '300px' }}>
          {!imageLoaded && (
            <div 
              className="position-absolute top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center"
              style={{ backgroundColor: '#f8f9fa' }}
            >
              <div className="spinner-border text-primary" role="status">
                <span className="visually-hidden">Loading...</span>
              </div>
            </div>
          )}
          <img 
            src={ `data:image/png;base64,${design.base64}`} //This is changed `data:image/png;base64,${response.data.final_templete}`
            alt={design.title}
            className="card-img-top h-100"
            style={{
              objectFit: 'cover',
              opacity: imageLoaded ? 1 : 0,
              transition: 'opacity 0.3s ease'
            }}
            onLoad={handleImageLoad}
          />
          
          {/* Action buttons overlay */}
          <div className="position-absolute top-0 end-0 m-3">
            {isNewlyGenerated && (
              <span className="badge bg-success me-2 px-2 py-1">
                <Sparkles size={12} className="me-1" />
                New
              </span>
            )}
            <button
              onClick={() => setIsLiked(!isLiked)}
              className={`btn btn-sm rounded-circle ${isLiked ? 'btn-danger' : 'btn-light'}`}
              style={{ width: '36px', height: '36px', padding: '0' }}
            >
              <Heart size={16} fill={isLiked ? 'currentColor' : 'none'} />
            </button>
          </div>

          {/* View count badge */}
          <div className="position-absolute bottom-0 start-0 m-3">
            <span className="badge bg-dark bg-opacity-75 d-flex align-items-center gap-1">
              <Eye size={12} />
              {design.views || Math.floor(Math.random() * 500) + 100}
            </span>
          </div>
        </div>
        
        <div className="card-body p-4">
          <div className="d-flex justify-content-between align-items-start mb-3">
            <div>
              <h5 className="card-title mb-1" style={{ color: '#213547', fontWeight: '600' }}>
                {design.title}
              </h5>
              <p className="card-text text-muted mb-0" style={{ fontSize: '0.9rem' }}>
                {design.description}
              </p>
            </div>
          </div>

          {/* Tags */}
          {design.tags && (
            <div className="mb-3">
              {design.tags.map((tag, tagIndex) => (
                <span 
                  key={tagIndex}
                  className="badge me-1 mb-1"
                  style={{
                    backgroundColor: '#e3f2fd',
                    color: '#1976d2',
                    fontSize: '0.75rem'
                  }}
                >
                  {tag}
                </span>
              ))}
            </div>
          )}

          {/* Action buttons */}
          <div className="d-flex gap-2">
            <button 
              className="btn btn-outline-primary btn-sm flex-fill d-flex align-items-center justify-content-center gap-1"
              style={{ borderRadius: '8px' }}
            >
              <Download size={14} />
              Download
            </button>
            <button 
              className="btn btn-outline-secondary btn-sm flex-fill d-flex align-items-center justify-content-center gap-1"
              style={{ borderRadius: '8px' }}
            >
              <Share2 size={14} />
              Share
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

const FilterBar = ({ activeFilter, setActiveFilter, designCount }) => {
  const filters = [
    { key: 'all', label: 'All Designs', count: designCount },
    { key: 'traditional', label: 'Traditional', count: Math.floor(designCount * 0.6) },
    { key: 'modern', label: 'Modern', count: Math.floor(designCount * 0.4) },
    { key: 'fusion', label: 'Fusion', count: Math.floor(designCount * 0.3) }
  ];

  return (
    <div className="card mb-4" style={{ borderRadius: '12px', border: 'none' }}>
      <div className="card-body p-3">
        <div className="d-flex flex-wrap gap-2 align-items-center justify-content-center">
          {filters.map(filter => (
            <button
              key={filter.key}
              onClick={() => setActiveFilter(filter.key)}
              className={`btn d-flex align-items-center gap-2 ${
                activeFilter === filter.key
                  ? 'btn-primary'
                  : 'btn-outline-secondary'
              }`}
              style={{
                borderRadius: '12px',
                fontWeight: '500',
                background: activeFilter === filter.key 
                  ? 'linear-gradient(135deg, #6f42c1 0%, #0d6efd 100%)' 
                  : 'transparent'
              }}
            >
              {filter.label}
              <span className={`badge ${
                activeFilter === filter.key ? 'bg-light text-primary' : 'bg-secondary'
              }`}>
                {filter.count}
              </span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

const DesignPage = (props) => {
  const [isLoading, setIsLoading] = useState(true);
  const [imagesLoaded, setImagesLoaded] = useState(0);
  const [activeFilter, setActiveFilter] = useState('all');
  const [newlyGenerated, setNewlyGenerated] = useState(null);
  const [allDesign , setAllDesigns] = useState([]);
  const [allDesignsLoaded, setAllDesignsLoaded] = useState(false);
  const navigate = useNavigate();

  // Get the newly generated design from props/navigation state
  useEffect(() => {
    console.log("props : ",props)
    
      
    
    const handleGenerateDesgin = async ()=>{
    const payload = {
      border: props.borderId,
      pallu: props.palluId,
      pattern: null,
      body: props.bodyId,
      prompt: props.prompt
    };
    try {
      console.log(payload)
      const response = await axios.post('http://localhost:5000/generate', payload);
      console.log('Backend response:', response.data);
  
      // Example: If your backend returns a URL to the generated image
      if (response.data.final_templete) {
        // Construct a new design object for the banner
        const newDesign = {
          src: `data:image/png;base64,${response.data.final_templete}`,
          title: "Your AI Saree",
          description: "AI-generated saree design based on your preferences",
          // Add any other fields you want
        };
        setNewlyGenerated(newDesign);
      }
      if (response.data.error) {
        console.log('Error: ' + response.data.error);
      } else {
        setIsLoading(false);
      }
      
    } catch (error) {
      console.log('Error generating design:', error);
      console.log('Failed to generate design. See console for details.');
    }
  }
    // Check if there's a newly generated design passed via navigation state
    if (props.location?.state?.generatedDesign) {
      setNewlyGenerated(props.location.state.generatedDesign);
    } else if (props.generatedDesign) {
      // Or passed via props
      setNewlyGenerated(props.generatedDesign);
    }
    handleGenerateDesgin()
  }
  , []);
async function getAllDesigns(){
    try {
      const response = await axios.get('http://localhost:5000/images'); 
      console.log(response.data.images);
    setAllDesigns(response.data.images);
    } catch (error) {
      console.log('Error getting all designs:', error);
    }
   
  }
  if(!allDesignsLoaded){
  setAllDesignsLoaded(true);
  getAllDesigns()}
  

  // Enhanced sample designs with more data
  const designImages = [
    {
      src: "https://images.unsplash.com/photo-1583394838336-acd977736f90?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=684&q=80",
      title: "Royal Peacock",
      description: "Traditional peacock motifs with golden borders",
      tags: ["Traditional", "Peacock", "Golden"],
      category: "traditional",
      views: 324
    },
    {
      src: "https://images.unsplash.com/photo-1583394838336-acd977736f90?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=684&q=80",
      title: "Modern Geometric",
      description: "Contemporary patterns with vibrant colors",
      tags: ["Modern", "Geometric", "Vibrant"],
      category: "modern",
      views: 256
    },
    {
      src: "https://images.unsplash.com/photo-1583394838336-acd977736f90?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=684&q=80",
      title: "Fusion Elegance",
      description: "Blend of traditional and modern elements",
      tags: ["Fusion", "Elegant", "Unique"],
      category: "fusion",
      views: 189
    },
    {
      src: "https://images.unsplash.com/photo-1583394838336-acd977736f90?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=684&q=80",
      title: "Floral Heritage",
      description: "Classic floral patterns with silk texture",
      tags: ["Traditional", "Floral", "Silk"],
      category: "traditional",
      views: 412
    },
    {
      src: "https://images.unsplash.com/photo-1583394838336-acd977736f90?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=684&q=80",
      title: "Minimalist Chic",
      description: "Simple yet sophisticated design",
      tags: ["Modern", "Minimalist", "Chic"],
      category: "modern",
      views: 178
    },
    {
      src: "https://images.unsplash.com/photo-1583394838336-acd977736f90?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=684&q=80",
      title: "Cultural Fusion",
      description: "Mix of regional traditional patterns",
      tags: ["Fusion", "Cultural", "Heritage"],
      category: "fusion",
      views: 295
    }
  ];

  // Combine newly generated design with existing designs
  const allDesigns = newlyGenerated 
    ? [newlyGenerated, ...designImages]
    : designImages;

  const filteredDesigns = activeFilter === 'all' 
    ? allDesigns 
    : allDesigns.filter(design => design.category === activeFilter);

  const handleImageLoad = () => {
    setImagesLoaded(prev => prev + 1);
  };

  const handleBackToHome = () => {
    navigate('/');
  };

  if (isLoading) {
    return <LoadingPage />;
  }

  return (
    <div className="min-vh-100 pt-5" style={{ background: 'linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)' }}>
      <div className="container py-4">
        {/* New Design Banner */}
        {newlyGenerated && <NewDesignBanner design={newlyGenerated} />}

        {/* Header */}
        <div className="text-center mb-5">
          <div className="d-flex align-items-center justify-content-center mb-3">
            <button
              onClick={handleBackToHome}
              className="btn btn-outline-secondary me-3 d-flex align-items-center gap-2"
              style={{ borderRadius: '12px' }}
            >
              <ArrowLeft size={16} />
              Back to Studio
            </button>
            <h1 
              className="display-4 fw-bold mb-0" 
              style={{ 
                background: 'linear-gradient(135deg, #6f42c1 0%, #0d6efd 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text'
              }}
            >
              Design Gallery
            </h1>
          </div>
          <p className="lead text-muted">
            {newlyGenerated ? 'Your new design is ready! Explore more designs below.' : 'Explore our AI-generated saree designs'}
          </p>
        </div>

        {/* Filter Bar */}
        <FilterBar 
          activeFilter={activeFilter}
          setActiveFilter={setActiveFilter}
          designCount={allDesigns.length}
        />

        {/* Stats Bar */}
        <div className="row mb-4">
          <div className="col-12">
            <div className="card" style={{ borderRadius: '12px', border: 'none' }}>
              <div className="card-body p-3">
                <div className="row text-center">
                  <div className="col-4">
                    <div className="d-flex align-items-center justify-content-center gap-2">
                      <Sparkles size={20} className="text-primary" />
                      <div>
                        <div className="fw-bold">{filteredDesigns.length}</div>
                        <small className="text-muted">Designs</small>
                      </div>
                    </div>
                  </div>
                  <div className="col-4">
                    <div className="d-flex align-items-center justify-content-center gap-2">
                      <Eye size={20} className="text-success" />
                      <div>
                        <div className="fw-bold">
                          {filteredDesigns.reduce((sum, design) => sum + (design.views || 0), 0)}
                        </div>
                        <small className="text-muted">Total Views</small>
                      </div>
                    </div>
                  </div>
                  <div className="col-4">
                    <div className="d-flex align-items-center justify-content-center gap-2">
                      <Heart size={20} className="text-danger" />
                      <div>
                        <div className="fw-bold">{Math.floor(filteredDesigns.length * 0.7)}</div>
                        <small className="text-muted">Liked</small>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Newly Generated Design Section */}
        <div className="mb-5">
          <div 
            className="card border-0 shadow-lg mb-4"
            style={{
              borderRadius: '20px',
              background: newlyGenerated 
                ? 'linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%)'
                : 'linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)',
              border: newlyGenerated 
                ? '2px solid #6f42c1'
                : '2px dashed #dee2e6'
            }}
          >
            <div className="card-header border-0 bg-transparent pt-4 pb-2">
              <div className="d-flex align-items-center justify-content-between">
                <div className="d-flex align-items-center">
                  {newlyGenerated ? (
                    <>
                      <div 
                        className="badge me-3 px-3 py-2"
                        style={{ 
                          background: 'linear-gradient(135deg, #6f42c1 0%, #0d6efd 100%)',
                          color: 'white',
                          fontSize: '0.9rem'
                        }}
                      >
                        <Sparkles size={16} className="me-2" />
                        Just Created
                      </div>
                      <h2 className="mb-0 fw-bold" style={{ color: '#6f42c1' }}>
                        Your Latest AI Creation
                      </h2>
                    </>
                  ) : (
                    <>
                      <div 
                        className="badge me-3 px-3 py-2 bg-secondary text-white"
                        style={{ fontSize: '0.9rem' }}
                      >
                        <Sparkles size={16} className="me-2" />
                        Create New
                      </div>
                      <h2 className="mb-0 fw-bold text-muted">
                        Ready to Create Your Design?
                      </h2>
                    </>
                  )}
                </div>
                <div className="text-muted">
                  <small>
                    {newlyGenerated ? 'Generated moments ago' : 'Start designing now'}
                  </small>
                </div>
              </div>
            </div>
            
            <div className="card-body px-4 pb-4">
              <div className="row g-4">
                <div className="col-12 col-lg-8 mx-auto">
                  {newlyGenerated ? (
                    <DesignCard
                      key={`new-${newlyGenerated.title || newlyGenerated.imageId || 'generated'}`}
                      design={newlyGenerated}
                      index={0}
                      onImageLoad={handleImageLoad}
                      isNewlyGenerated={true}
                    />
                  ) : (
                    <div 
                      className="card h-100 border-0"
                      style={{
                        borderRadius: '16px',
                        background: 'linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%)',
                        minHeight: '400px'
                      }}
                    >
                      <div className="card-body d-flex flex-column align-items-center justify-content-center text-center p-5">
                        <div 
                          className="mb-4 d-flex align-items-center justify-content-center"
                          style={{
                            width: '80px',
                            height: '80px',
                            background: 'linear-gradient(135deg, #6f42c1 0%, #0d6efd 100%)',
                            borderRadius: '50%',
                            opacity: '0.1'
                          }}
                        >
                          <Sparkles size={40} className="text-primary" />
                        </div>
                        <h4 className="text-muted mb-3">No Design Generated Yet</h4>
                        <p className="text-muted mb-4 lead">
                          Start creating your unique AI-generated saree design. 
                          Your latest creation will appear here.
                        </p>
                        <button
                          onClick={handleBackToHome}
                          className="btn btn-lg px-4 py-3 d-flex align-items-center gap-2"
                          style={{
                            background: 'linear-gradient(135deg, #6f42c1 0%, #0d6efd 100%)',
                            border: 'none',
                            borderRadius: '12px',
                            color: 'white',
                            fontWeight: '600'
                          }}
                        >
                          <Sparkles size={20} />
                          Create Your First Design
                        </button>
                        <small className="text-muted mt-3">
                          Use AI to generate stunning saree patterns
                        </small>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Divider between sections */}
        <div className="text-center mb-5">
          <div className="d-inline-flex align-items-center gap-3">
            <div style={{ width: '100px', height: '2px', background: 'linear-gradient(to right, transparent, #dee2e6, transparent)' }}></div>
            <span className="text-muted fw-medium">
              {newlyGenerated ? 'Explore More Designs' : 'Browse Our Gallery'}
            </span>
            <div style={{ width: '100px', height: '2px', background: 'linear-gradient(to right, transparent, #dee2e6, transparent)' }}></div>
          </div>
        </div>

        {/* Other Designs Section */}
        <div className="mb-4">
          <div className="d-flex align-items-center justify-content-between mb-4">
            <h3 className="mb-0" style={{ color: '#495057' }}>
              {newlyGenerated ? 'More Designs You Might Like' : 'All '}
            </h3>
            {newlyGenerated && (
              <span className="text-muted">
                <Eye size={16} className="me-1" />
                Discover similar styles
              </span>
            )}
          </div>
          
          <div className="row g-4">
            {/* Filter out the newly generated design from the main grid */}
            {(() => {
              const otherDesigns = newlyGenerated 
                ? filteredDesigns.slice(1) // Skip the first item (newly generated)
                : filteredDesigns; // Show all designs if no newly generated one
              
              if (otherDesigns.length === 0) {
                return (
                  <div className="col-12">
                    <div className="text-center py-5">
                      <Sparkles size={48} className="text-muted mb-3" />
                      <h4 className="text-muted">No designs found</h4>
                      <p className="text-muted">Try selecting a different filter</p>
                    </div>
                  </div>
                );
              }

              return allDesign.map((design, index) => (
                <DesignCard
                  key={`${design.title || design.imageId || index}`}
                  design={design}
                  index={newlyGenerated ? index + 1 : index} // Adjust index only if there's a newly generated design
                  onImageLoad={handleImageLoad}
                  isNewlyGenerated={false}
                />
              ));
            })()}
          </div>
        </div>

        {/* Load More Button */}
        {filteredDesigns.length > 0 && (
          <div className="text-center mt-5">
            <button
              className="btn btn-lg px-5"
              style={{
                background: 'linear-gradient(135deg, #6f42c1 0%, #0d6efd 100%)',
                border: 'none',
                borderRadius: '12px',
                color: 'white',
                fontWeight: '600'
              }}
            >
              <Sparkles size={20} className="me-2" />
              Load More Designs
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default DesignPage;