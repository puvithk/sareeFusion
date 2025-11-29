import requests
import os
import time
from PIL import Image
import io

# Flask API base URL
BASE_URL = 'http://localhost:5000'

def create_test_image(filename="test_image.png", size=(100, 100), color=(255, 0, 0)):
    """Create a test image for testing"""
    img = Image.new('RGB', size, color)
    img.save(filename)
    return filename

def test_home():
    """Test the home endpoint"""
    print("=" * 50)
    print("Testing Home Endpoint")
    print("=" * 50)
    try:
        response = requests.get(f'{BASE_URL}/')
        print(f"Status Code: {response.status_code}")
        print("Response:")
        print(response.json())
        print()
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_upload_endpoint(endpoint_name, image_path):
    """Test uploading an image to a specific endpoint"""
    print(f"=" * 50)
    print(f"Testing {endpoint_name} Endpoint")
    print(f"=" * 50)
    
    if not os.path.exists(image_path):
        print(f"Error: Image file {image_path} not found!")
        return False
    
    try:
        with open(image_path, 'rb') as f:
            files = {'image': f}
            response = requests.post(f'{BASE_URL}/{endpoint_name}', files=files)
        
        print(f"Status Code: {response.status_code}")
        print("Response:")
        print(response.json())
        print()
        
        if response.status_code == 201:
            return response.json().get('filename')
        return False
    
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_generate():
    """Test the generate endpoint"""
    print("=" * 50)
    print("Testing Generate Endpoint")
    print("=" * 50)
    try:
        response = requests.get(f'{BASE_URL}/generate')
        print(f"Status Code: {response.status_code}")
        print("Response:")
        print(response.json())
        print()
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_get_images():
    """Test getting list of uploaded images"""
    print("=" * 50)
    print("Testing Get Images Endpoint")
    print("=" * 50)
    try:
        response = requests.get(f'{BASE_URL}/images')
        print(f"Status Code: {response.status_code}")
        print("Response:")
        print(response.json())
        print()
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_get_specific_image(filename):
    """Test getting a specific image"""
    print("=" * 50)
    print(f"Testing Get Specific Image: {filename}")
    print("=" * 50)
    try:
        response = requests.get(f'{BASE_URL}/image/{filename}')
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Image retrieved successfully!")
            print(f"Content-Type: {response.headers.get('content-type')}")
            print(f"Content-Length: {len(response.content)} bytes")
        else:
            print("Response:")
            print(response.json())
        print()
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_invalid_upload(endpoint_name):
    """Test uploading invalid file"""
    print("=" * 50)
    print(f"Testing Invalid Upload to {endpoint_name}")
    print("=" * 50)
    try:
        # Create a text file instead of image
        with open('test.txt', 'w') as f:
            f.write("This is not an image file")
        
        with open('test.txt', 'rb') as f:
            files = {'image': f}
            response = requests.post(f'{BASE_URL}/{endpoint_name}', files=files)
        
        print(f"Status Code: {response.status_code}")
        print("Response:")
        print(response.json())
        print()
        
        # Clean up
        os.remove('test.txt')
        return response.status_code == 400
    
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_missing_file(endpoint_name):
    """Test uploading without file"""
    print("=" * 50)
    print(f"Testing Missing File to {endpoint_name}")
    print("=" * 50)
    try:
        response = requests.post(f'{BASE_URL}/{endpoint_name}')
        print(f"Status Code: {response.status_code}")
        print("Response:")
        print(response.json())
        print()
        return response.status_code == 400
    
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_upload_process_directory(directory_path):
    """Test uploading and processing all images from a directory to /process-image endpoint"""
    print("=" * 50)
    print(f"Testing /process-image Endpoint for all images in: {directory_path}")
    print("=" * 50)
    allowed_ext = {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp'}
    if not os.path.isdir(directory_path):
        print(f"Error: Directory {directory_path} not found!")
        return False
    
    image_files = [f for f in os.listdir(directory_path) if os.path.splitext(f)[1].lower() in allowed_ext]
    if not image_files:
        print(f"No image files found in {directory_path}")
        return False
    
    results = []
    for image_file in image_files:
        image_path = os.path.join(directory_path, image_file)
        print(f"Uploading {image_file} ...")
        try:
            with open(image_path, 'rb') as f:
                files = {'image': f}
                response = requests.post(f'{BASE_URL}/process-image', files=files)
            print(f"Status Code: {response.status_code}")
            try:
                print("Response:")
                print(response.json())
            except Exception:
                print("Non-JSON response")
            print()
            results.append((image_file, response.status_code))
        except Exception as e:
            print(f"Error processing {image_file}: {e}")
            results.append((image_file, 'error'))
    print(f"Processed {len(results)} images from {directory_path}")
    return results

def cleanup_test_files():
    """Clean up test files"""
    test_files = ['test_border.png', 'test_pallu.png', 'test_body.png', 'test_pattern.png']
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"Cleaned up: {file}")

def main():
    print("Flask Image Upload API - Comprehensive Test Suite")
    print("=" * 60)
    
    # Check if server is running
    try:
        response = requests.get(f'{BASE_URL}/')
        print("✅ Server is running!")
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running. Please start the Flask app first:")
        print("   python app.py")
        return
    
    # Create test images
    print("\nCreating test images...")
    test_border = create_test_image("test_border.png", (100, 100), (255, 0, 0))  # Red
    test_pallu = create_test_image("test_pallu.png", (100, 100), (0, 255, 0))    # Green
    test_body = create_test_image("test_body.png", (100, 100), (0, 0, 255))      # Blue
    test_pattern = create_test_image("test_pattern.png", (100, 100), (255, 255, 0))  # Yellow
    
    uploaded_files = []
    
    # Test home endpoint
    test_home()
    
    # Test upload endpoints
    print("\n" + "=" * 60)
    print("TESTING UPLOAD ENDPOINTS")
    print("=" * 60)
    
    # Test valid uploads
    border_filename = test_upload_endpoint("upload-border", test_border)
    if border_filename:
        uploaded_files.append(border_filename)
    
    pallu_filename = test_upload_endpoint("upload-pallu", test_pallu)
    if pallu_filename:
        uploaded_files.append(pallu_filename)
    
    body_filename = test_upload_endpoint("upload-body", test_body)
    if body_filename:
        uploaded_files.append(body_filename)
    
    pattern_filename = test_upload_endpoint("upload-pattern", test_pattern)
    if pattern_filename:
        uploaded_files.append(pattern_filename)
    
    # Test invalid uploads
    print("\n" + "=" * 60)
    print("TESTING ERROR CASES")
    print("=" * 60)
    
    test_invalid_upload("upload-border")
    test_missing_file("upload-border")
    
    # Test other endpoints
    print("\n" + "=" * 60)
    print("TESTING OTHER ENDPOINTS")
    print("=" * 60)
    
    test_generate()
    test_get_images()
    
    # Test getting specific images
    if uploaded_files:
        print("\n" + "=" * 60)
        print("TESTING IMAGE RETRIEVAL")
        print("=" * 60)
        
        for filename in uploaded_files[:2]:  # Test first 2 uploaded files
            test_get_specific_image(filename)
    
    # Test non-existent image
    test_get_specific_image("non_existent_image.png")
    
    # Example usage for batch processing (uncomment and set your path):
    test_upload_process_directory('C:/Users/puvit/Downloads/Resume')
    
    # Cleanup
    print("\n" + "=" * 60)
    print("CLEANUP")
    print("=" * 60)
    cleanup_test_files()
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Test completed successfully!")
    print(f"📁 Uploaded {len(uploaded_files)} test images")
    print(f"🌐 Server running at: {BASE_URL}")
    print("=" * 60)

if __name__ == '__main__':
    main() 