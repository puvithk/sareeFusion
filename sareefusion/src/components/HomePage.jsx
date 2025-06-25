import React, { useRef, useState, useEffect } from 'react';
import { Upload, Image, X, Plus, Sparkles, Palette } from 'lucide-react';
import axios from 'axios'
import { useNavigate } from 'react-router-dom';
const GalleryUpload = ({ onImageDrop, isLoading }) => {
  const inputRef = useRef();
  const [isDragActive, setIsDragActive] = useState(false);

  const handleBoxClick = () => {
    inputRef.current.click();
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragActive(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragActive(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragActive(false);
    const files = Array.from(e.dataTransfer.files);
    const validFiles = files.filter(file => 
      file.type === 'image/png' || file.type === 'image/jpeg' || file.type === 'image/jpg'
    );
    if (validFiles.length > 0) {
      onImageDrop && onImageDrop(validFiles);
    }
  };

  const handleFileChange = (e) => {
    const files = Array.from(e.target.files);
    if (files.length > 0) {
      onImageDrop && onImageDrop(files);
    }
  };

  return (
    <button
      onClick={handleBoxClick}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      disabled={isLoading}
      className={`btn d-flex align-items-center gap-2 ${
        isDragActive 
          ? 'btn-outline-primary border-primary' 
          : 'btn-outline-secondary'
      }`}
      style={{
        borderStyle: 'dashed',
        borderWidth: '2px',
        borderRadius: '12px',
        background: isLoading ? '#f8f9fa' : 'linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%)',
        opacity: isLoading ? 0.6 : 1,
        cursor: isLoading ? 'not-allowed' : 'pointer',
        transition: 'all 0.2s ease'
      }}
    >
      <input
        type="file"
        ref={inputRef}
        style={{ display: 'none' }}
        accept=".png,.jpg,.jpeg"
        onChange={handleFileChange}
        multiple
        disabled={isLoading}
      />
      {isLoading ? (
        <div className="spinner-border spinner-border-sm text-primary" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      ) : (
        <Plus size={20} className="text-primary" />
      )}
      <span className="text-primary fw-medium">
        {isLoading ? 'Adding...' : 'Add to Gallery'}
      </span>
    </button>
  );
};

const UploadBox = ({ label, elementType, onImageDrop, galleryImages, elementImageId, setElementImageId, isActive }) => {
  const inputRef = useRef();
  const [isDragActive, setIsDragActive] = useState(false);
  const [previewImage, setPreviewImage] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showGalleryModal, setShowGalleryModal] = useState(false);

  useEffect(() => {
    if (elementImageId) {
      const found = galleryImages.find(img => img.imageId === elementImageId);
      setPreviewImage(found ? found.dataUrl : null);
    } else {
      setPreviewImage(null);
    }
  }, [elementImageId, galleryImages]);

  const handleDrop = async (e) => {
    e.preventDefault();
    setIsDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      if (file && (file.type === 'image/png' || file.type === 'image/jpeg' || file.type === 'image/jpg')) {
        await handleFileUpload(file);
      }
    } else {
      const imageId = e.dataTransfer.getData('gallery-imageId');
      if (imageId) {
        setElementImageId(imageId);
      } else {
        const imageUrl = e.dataTransfer.getData('text/plain');
        if (imageUrl) {
          const found = galleryImages.find(img => img.dataUrl === imageUrl);
          if (found) setElementImageId(found.imageId);
        }
      }
    }
  };

  const handleBoxClick = () => {
    if (!isLoading) {
      setShowGalleryModal(true);
    }
  };

  const handleBrowseClick = (e) => {
    e.stopPropagation();
    inputRef.current.click();
  };

  const handleDragOver = (e) => {
    if (!isLoading) {
      e.preventDefault();
      setIsDragActive(true);
    }
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragActive(false);
  };

  const handleFileUpload = async (file) => {
    const reader = new FileReader();
    reader.onload = async (e) => {
      const dataUrl = e.target.result;
      const found = galleryImages.find(img => img.dataUrl === dataUrl);
      if (found) {
        setElementImageId(found.imageId);
        setPreviewImage(found.dataUrl);
      } else {
        setIsLoading(true);
        try {
          const formData = new FormData();
          formData.append('image', file);
          // Replace with your actual API endpoint
          const response = await axios.post('http://localhost:5000/process-image', formData);
          const imageId = response.data.image_id;
         
          onImageDrop({ imageId, dataUrl });
          setElementImageId(imageId);
          setPreviewImage(dataUrl);
        } catch (err) {
          alert('Failed to upload/process image');
        }
        setIsLoading(false);
      }
    };
    reader.readAsDataURL(file);
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      handleFileUpload(file);
    }
  };

  const getElementIcon = () => {
    switch (elementType) {
      case 'pattern': return <Sparkles size={32} className="text-primary" />;
      case 'border': return <div style={{ width: '32px', height: '32px', border: '4px solid #0d6efd', borderRadius: '4px' }} />;
      case 'pallu': return <Palette size={32} className="text-primary" />;
      case 'body': return <Image size={32} className="text-primary" />;
      default: return <Upload size={32} className="text-primary" />;
    }
  };

  const GalleryModal = () => (
    <div 
      className="modal fade show d-block"
      style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}
      onClick={() => setShowGalleryModal(false)}
    >
      <div className="modal-dialog modal-lg modal-dialog-centered">
        <div 
          className="modal-content"
          onClick={e => e.stopPropagation()}
        >
          <div className="modal-header">
            <h5 className="modal-title">Select from Gallery</h5>
            <button
              type="button"
              className="btn-close"
              onClick={() => setShowGalleryModal(false)}
            ></button>
          </div>
          <div className="modal-body">
            <div className="row g-3">
              {galleryImages.length === 0 && (
                <div className="col-12 text-center py-4 text-muted">
                  <Image size={48} className="mb-3" />
                  <p>No images in gallery yet</p>
                </div>
              )}
              {galleryImages.map((img, index) => (
                <div key={img.imageId} className="col-6 col-md-4 col-lg-3">
                  <div
                    className="card h-100 shadow-sm"
                    style={{ cursor: 'pointer', transition: 'transform 0.2s' }}
                    onClick={() => {
                      setElementImageId(img.imageId);
                      setShowGalleryModal(false);
                    }}
                    onMouseOver={(e) => e.currentTarget.style.transform = 'scale(1.05)'}
                    onMouseOut={(e) => e.currentTarget.style.transform = 'scale(1)'}
                  >
                    <img 
                      src={img.dataUrl} 
                      alt={`Gallery ${index + 1}`}
                      className="card-img-top"
                      style={{ height: '100px', objectFit: 'cover' }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <>
      {showGalleryModal && <GalleryModal />}
      <div
        onClick={handleBoxClick}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`card h-100 ${isDragActive ? 'border-primary' : isActive ? 'border-info' : 'border-secondary'}`}
        style={{
          borderStyle: 'dashed',
          borderWidth: '2px',
          cursor: isLoading ? 'not-allowed' : 'pointer',
          height: '250px',
          background: isActive 
            ? 'linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%)' 
            : 'linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%)',
          opacity: isLoading ? 0.6 : 1,
          transition: 'all 0.3s ease',
          overflow: 'hidden'
        }}
      >
        <input
          type="file"
          ref={inputRef}
          style={{ display: 'none' }}
          accept=".png,.jpg,.jpeg"
          onChange={handleFileChange}
          disabled={isLoading}
        />
        
        {isLoading ? (
          <div className="card-body d-flex flex-column align-items-center justify-content-center">
            <div className="spinner-border text-primary mb-3" role="status">
              <span className="visually-hidden">Loading...</span>
            </div>
            <span className="text-primary fw-medium">Processing...</span>
          </div>
        ) : previewImage ? (
          <div className="position-relative h-100">
            <img 
              src={previewImage} 
              alt="Preview" 
              className="card-img-top h-100"
              style={{ objectFit: 'cover' }}
            />
            <button
              onClick={(e) => {
                e.stopPropagation();
                setElementImageId(null);
              }}
              className="btn btn-light btn-sm position-absolute top-0 end-0 m-2 rounded-circle"
              style={{ width: '30px', height: '30px', padding: '0' }}
            >
              <X size={16} />
            </button>
            <div className="position-absolute bottom-0 start-0 m-2">
              <span className="badge bg-white text-dark">{label}</span>
            </div>
          </div>
        ) : (
          <div className="card-body d-flex flex-column align-items-center justify-content-center text-center">
            {getElementIcon()}
            <h6 className="card-title mt-3 mb-3">{label}</h6>
            <div className="d-grid gap-2 w-100">
              <button
                onClick={handleBrowseClick}
                className="btn btn-primary btn-sm"
              >
                Browse Files
              </button>
              <button
                onClick={e => { e.stopPropagation(); setShowGalleryModal(true); }}
                className="btn btn-outline-primary btn-sm"
              >
                From Gallery
              </button>
            </div>
            <small className="text-muted mt-2">PNG, JPG, JPEG</small>
          </div>
        )}
      </div>
    </>
  );
};

const ImageGallery = ({ images, onImageRemove }) => {
  return (
    <div className="card mb-4">
      <div className="card-header bg-light">
        <div className="d-flex align-items-center gap-2">
          <Image size={20} className="text-primary" />
          <h5 className="card-title mb-0">Image Gallery</h5>
          <span className="badge bg-primary">{images.length} images</span>
        </div>
      </div>
      <div className="card-body">
        {images.length === 0 ? (
          <div className="text-center py-4 text-muted">
            <Image size={48} className="mb-3" />
            <p className="mb-1">No images uploaded yet</p>
            <small>Upload images to see them here</small>
          </div>
        ) : (
          <div className="d-flex gap-3 overflow-auto pb-2" style={{ minHeight: '120px' }}>
            {images.map((img, index) => (
              <div
                key={img.imageId}
                className="position-relative flex-shrink-0"
                style={{ width: '120px', height: '120px' }}
                draggable
                onDragStart={e => {
                  e.dataTransfer.setData('gallery-imageId', img.imageId);
                  e.dataTransfer.setData('text/plain', img.dataUrl);
                }}
              >
                <div 
                  className="card h-100 shadow-sm"
                  style={{ cursor: 'pointer', transition: 'transform 0.2s' }}
                  onMouseOver={(e) => e.currentTarget.style.transform = 'scale(1.05)'}
                  onMouseOut={(e) => e.currentTarget.style.transform = 'scale(1)'}
                >
                  <img
                    src={img.dataUrl}
                    alt={`Gallery ${index + 1}`}
                    className="card-img-top h-100"
                    style={{ objectFit: 'cover' }}
                  />
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onImageRemove(index);
                  }}
                  className="btn btn-danger btn-sm position-absolute top-0 end-0 m-1 rounded-circle"
                  style={{ width: '25px', height: '25px', padding: '0', fontSize: '12px' }}
                >
                  <X size={12} />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

const Homepage = (props) => {
  const [gallery, setGallery] = useState([]);
  const [elementImageIds, setElementImageIds] = useState({
    border: null,
    pallu: null,
    pattern: null,
    body: null
  });
  const [designPrompt, setDesignPrompt] = useState("");
  const [galleryLoading, setGalleryLoading] = useState(false);
  const [activeElement, setActiveElement] = useState('pattern');
  const navigator = useNavigate()
  const handleGalleryImageUpload = async (files) => {
    setGalleryLoading(true);
    for (const file of files) {
      const reader = new FileReader();
      reader.onload = async (e) => {
        const dataUrl = e.target.result;
        if (!gallery.some(img => img.dataUrl === dataUrl)) {
          try {
            // Replace with your actual API endpoint
            const formData = new FormData();
            formData.append('image', file);
            const response = await axios.post('http://localhost:5000/process-image', formData);
            const imageId = response.data.image_id;
           
            
            setGallery(prev => [...prev, { imageId, dataUrl }]);
          } catch (err) {
            alert('Failed to upload/process image: ' + err);
          }
        }
      };
      reader.readAsDataURL(file);
    }
    setTimeout(() => setGalleryLoading(false), 800);
  };

  const setElementImageId = (element) => (imageId) => {
    setElementImageIds(prev => ({ ...prev, [element]: imageId }));
    setActiveElement(element);
  };

  const handleImageRemove = (index) => {
    setGallery(prev => prev.filter((_, i) => i !== index));
  };

  const handleGenerateDesign = async () => {
    props.setBodyId(elementImageIds.body)
   props.setBorderId(elementImageIds.border)
    props.setPalluId(elementImageIds.pallu)
    navigator('/designs')
    // props.setBodyId(elementImageIds.body)
    // props.setBorderId(elementImageIds.border)
    // props.setPalluId(elementImageIds.pallu)
  //   const payload = {
  //     border: elementImageIds.border,
  //     pallu: elementImageIds.pallu,
  //     pattern: elementImageIds.pattern,
  //     body: elementImageIds.body,
  //     prompt: designPrompt
  //   };
  //   try {
  //     navigator('/designs')
  //     const response = await axios.post('http://localhost:5000/generate', payload);
  //     console.log('Backend response:', response.data);
  
  //     // Example: If your backend returns a URL to the generated image
  //     if (response.data.generated_image_url) {
  //       // Show the image or do something with the URL
  //       alert('Design generated! See the result.');
  //       // You can set this URL in your component state to display the image
  //       // setGeneratedImageUrl(response.data.generated_image_url);
  //     } else if (response.data.error) {
  //       alert('Error: ' + response.data.error);
  //     } else {
  //       alert('Design generation started! (Check console for details)');
  //     }
  //   } catch (error) {
  //     console.error('Error generating design:', error);
  //     alert('Failed to generate design. See console for details.');
  //   }
  };
  const elements = [
    { key: 'pattern', label: 'Pattern', icon: Sparkles },
    { key: 'border', label: 'Border', icon: Upload },
    { key: 'pallu', label: 'Pallu', icon: Palette },
    { key: 'body', label: 'Body', icon: Image },
  ];

  return (
    <div className="min-vh-100" style={{ background: 'linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)' }}>
      <div className="container py-4">
        {/* Header */}
        <div className="text-center mb-5">
          <h1 className="display-4 fw-bold mb-2" style={{ 
            background: 'linear-gradient(135deg, #6f42c1 0%, #0d6efd 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text'
          }}>
            Saree Design Studio
          </h1>
          <p className="lead text-muted">Create beautiful saree designs with AI</p>
        </div>

        {/* Element Selection and Gallery Upload */}
        <div className="row mb-4">
          <div className="col-12">
            <div className="d-flex justify-content-center align-items-center flex-wrap gap-3 mb-3">
              {/* Element Selection Buttons */}
              <div className="d-flex flex-wrap gap-2">
                {elements.map(({ key, label, icon: Icon }) => (
                  <button
                    key={key}
                    onClick={() => setActiveElement(key)}
                    className={`btn d-flex align-items-center gap-2 ${
                      activeElement === key
                        ? 'btn-primary shadow'
                        : 'btn-outline-secondary'
                    }`}
                    style={{
                      borderRadius: '12px',
                      fontWeight: '500',
                      background: activeElement === key 
                        ? 'linear-gradient(135deg, #6f42c1 0%, #0d6efd 100%)' 
                        : 'transparent'
                    }}
                  >
                    <Icon size={16} />
                    {label}
                  </button>
                ))}
              </div>
              
              {/* Separator */}
              <div style={{ 
                height: '30px', 
                width: '2px', 
                background: 'linear-gradient(135deg, #dee2e6 0%, #adb5bd 100%)',
                borderRadius: '1px'
              }}></div>
              
              {/* Gallery Upload Button */}
              <GalleryUpload onImageDrop={handleGalleryImageUpload} isLoading={galleryLoading} />
            </div>
          </div>
        </div>

        {/* Gallery */}
        <div className="row mb-4">
          <div className="col-12">
            <ImageGallery 
              images={gallery} 
              onImageRemove={handleImageRemove}
            />
          </div>
        </div>

        {/* Upload Boxes */}
        <div className="row g-4 mb-5">
          {elements.map(({ key, label }) => (
            <div key={key} className="col-12 col-md-6 col-lg-3">
              <UploadBox
                label={label}
                elementType={key}
                galleryImages={gallery}
                elementImageId={elementImageIds[key]}
                setElementImageId={setElementImageId(key)}
                isActive={activeElement === key}
                onImageDrop={(imageData) => {
                  setGallery(prev => [...prev, imageData]);
                }}
              />
            </div>
          ))}
        </div>

        {/* Prompt and Generate */}
        <div className="row">
          <div className="col-12">
            <div className="card shadow-sm">
              <div className="card-body p-4">
                <div className="row justify-content-center">
                  <div className="col-12 col-md-8 col-lg-6">
                    <h5 className="text-center mb-4">Design Prompt</h5>
                    <div className="input-group mb-4">
                      <input
                        type="text"
                        className="form-control form-control-lg"
                        value={designPrompt}
                        onChange={e => setDesignPrompt(e.target.value)}
                        placeholder="Describe your dream saree design..."
                        style={{ borderRadius: '12px 0 0 12px' }}
                      />
                      <span className="input-group-text" style={{ borderRadius: '0 12px 12px 0' }}>
                        <Sparkles size={20} className="text-muted" />
                      </span>
                    </div>
                    <div className="text-center">
                      <button
                        onClick={handleGenerateDesign}
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
                        Generate Design
                      </button>
                    </div>
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

export default Homepage;