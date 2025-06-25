from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
import uuid
import cv2
from PIL import Image
from Extracting_Element.extraction import SegmentationModel, Processing
from Genereating import new
from Proccessing.crop_image import CropCenter 
from Genereating.new import GenerateSaree 
from Genereating.generateSaree import GenerateComplete
from threading import Thread
from dotenv import load_dotenv
import base64
import random
from io import BytesIO
load_dotenv()
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
UPLOAD_FOLDER = 'uploads'
UPLOAD_PARTS = 'upload_parts'
UPLOAD_TEMPLET = 'templete'
UPLOAD_SAREE = 'saree'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
dir_path = os.path.dirname(os.path.realpath(__file__))
# Create uploads directory if it doesn't exist
os.makedirs(os.path.join(dir_path,UPLOAD_FOLDER), exist_ok=True)
os.makedirs(os.path.join(dir_path,  UPLOAD_PARTS) , exist_ok=True)
os.makedirs(os.path.join(dir_path,UPLOAD_TEMPLET), exist_ok=True)
os.makedirs(os.path.join(dir_path,  UPLOAD_SAREE) , exist_ok=True)
app.config['UPLOAD_FOLDER'] = os.path.join(dir_path,UPLOAD_FOLDER)
app.config['UPLOAD_PARTS'] =os.path.join(dir_path,  UPLOAD_PARTS)
app.config['UPLOAD_TEMPLET'] = os.path.join(dir_path , UPLOAD_TEMPLET)
app.config['UPLOAD_SAREE'] = os.path.join(dir_path , UPLOAD_SAREE)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
#segmentation_model = SegmentationModel('backend/Models/segmentation_model_weights1.pth', n_classes=5)
post_processing = Processing()
cropCenter = CropCenter()
generateSaree = GenerateSaree()
generetorFull = GenerateComplete()
def allowed_file(filename):
    """Check if the file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

import os

def get_specific_file_in_folder(folder_path, prefix):
    """
    Return the file in the folder that starts with the given prefix (e.g., 'Body0'),
    or None if not found.
    """
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        return None
    for f in os.listdir(folder_path):
        if f.startswith(prefix):
            return os.path.join(folder_path, f)
    return None
@app.route('/')
def home():
    """Home endpoint"""
    return jsonify({
        'message': 'Flask Image Upload API',
        'endpoints': {
            'upload_image': '/upload-image',
            'get_images': '/images'
        }
    })

@app.route('/process-image', methods=['POST'])
def process_image():
    """Endpoint to receive and save images"""
    try:
        # Check if the post request has the file part
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        imageId = uuid.uuid4().hex
        print(imageId)
        # If user does not select file, browser also submits an empty part without filename
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        print("Came here")
        if file and allowed_file(file.filename):
            # Generate a unique filename to avoid conflicts
            filename = secure_filename(file.filename)
            unique_filename = f"{imageId}_{filename}"
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            
            # Save the uploaded file first
            file.save(save_path)
            
            # Create a directory for the extracted parts
            parts_dir = os.path.join(app.config['UPLOAD_PARTS'], f"{imageId}_parts")
            os.makedirs(parts_dir, exist_ok=True)
            
            # Run segmentation model on the uploaded file
            #result, image = segmentation_model.predict(save_path)
            #track_parts = post_processing.extract_show(image, result)
            try:
                image = Image.open(save_path).convert('RGB')
            except Exception as e:
                print(e)
            track_parts = post_processing.extract_with_yolo(image)
            print(track_parts)
            print("HEy guys ")
            try:
                for class_name, class_images in track_parts.items():
                    for  i ,image  in enumerate(class_images):
                        print(i)
                        print(image)
                        image.save(os.path.join(parts_dir, class_name + str(i)+".png"))
                        
                        #cv2.imwrite((os.path.join(parts_dir, class_name + str(i)+".png")) , image)
                for i in track_parts:
                    print(len(i))
            except Exception as e:
                print(f"{e}FILE")
            
            return jsonify({
                'message': 'Image uploaded and processed successfully',
                'filename': unique_filename,
                'original_filename': filename,
                'filepath': save_path,
                'parts_dir': parts_dir,
                'image_id': imageId
            }), 201
        else:
            return jsonify({
                'error': 'File type not allowed. Allowed types: ' + ', '.join(ALLOWED_EXTENSIONS)
            }), 400
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/upload-pallu', methods=['POST'])
def upload_pallu():
    
    """Endpoint to receive and save images"""
    try:
        # Check if the post request has the file part
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        
        # If user does not select file, browser also submits an empty part without filename
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            # Generate a unique filename to avoid conflicts
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            
            # Save the file
            file.save(filepath)
            
            return jsonify({
                'message': 'Image uploaded successfully',
                'filename': unique_filename,
                'original_filename': filename,
                'filepath': filepath
            }), 201
        
        else:
            return jsonify({
                'error': 'File type not allowed. Allowed types: ' + ', '.join(ALLOWED_EXTENSIONS)
            }), 400
    
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/upload-body', methods=['POST'])
def upload_body():
    """Endpoint to receive and save images"""
    try:
        # Check if the post request has the file part
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        
        # If user does not select file, browser also submits an empty part without filename
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            # Generate a unique filename to avoid conflicts
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            
            # Save the file
            file.save(filepath)
            
            return jsonify({
                'message': 'Image uploaded successfully',
                'filename': unique_filename,
                'original_filename': filename,
                'filepath': filepath
            }), 201
        
        else:
            return jsonify({
                'error': 'File type not allowed. Allowed types: ' + ', '.join(ALLOWED_EXTENSIONS)
            }), 400
    
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500
@app.route('/upload-pattern', methods=['POST'])
def upload_pattern():
        """Endpoint to receive and save images"""
        try:
            # Check if the post request has the file part
            if 'image' not in request.files:
                return jsonify({'error': 'No image file provided'}), 400
            
            file = request.files['image']
            
            # If user does not select file, browser also submits an empty part without filename
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            if file and allowed_file(file.filename):
                # Generate a unique filename to avoid conflicts
                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                
                # Save the file
                file.save(filepath)
                
                return jsonify({
                    'message': 'Image uploaded successfully',
                    'filename': unique_filename,
                    'original_filename': filename,
                    'filepath': filepath
                }), 201
            
            else:
                return jsonify({
                    'error': 'File type not allowed. Allowed types: ' + ', '.join(ALLOWED_EXTENSIONS)
                }), 400
        
        except Exception as e:
            return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    print(data)
    borderImgId = data['border']
    palluImgId = data['pallu']
    patternImgId = data['pattern']
    bodyImgId = data['body']

    # Construct the folder paths
    border_folder = os.path.join(app.config['UPLOAD_PARTS'], f"{borderImgId}_parts")
    pallu_folder = os.path.join(app.config['UPLOAD_PARTS'], f"{palluImgId}_parts")
    pattern_folder = os.path.join(app.config['UPLOAD_PARTS'], f"{patternImgId}_parts")
    body_folder = os.path.join(app.config['UPLOAD_PARTS'], f"{bodyImgId}_parts")

    # Get the specific files
    border_file = get_specific_file_in_folder(border_folder, "Border0")
    pallu_file = get_specific_file_in_folder(pallu_folder, "Pallu0")
    pattern_file = get_specific_file_in_folder(pattern_folder, "Pattern0")
    body_file = get_specific_file_in_folder(body_folder, "Body0")

    border_image = Image.open(border_file).convert("RGB")
    pallu_image = Image.open(pallu_file).convert("RGB")
    body_image = Image.open(body_file).convert("RGB")


    cropperd_border = cropCenter.crop_pre_region(border_image)
    # Resize so height=100, width is scaled to maintain aspect ratio
    target_height = 200
    aspect_ratio = cropperd_border.width / cropperd_border.height
    target_width = int(target_height * aspect_ratio)
    cropperd_border = cropperd_border.resize((target_width, target_height))
    saree =  generateSaree.tempelete(cropperd_border , pallu_image , body_image)
    print("Border file:", border_file)
    print("Pallu file:", pallu_file)
    print("Pattern file:", pattern_file)
    print("Body file:", body_file)
    print("Final_templete" , saree)
    saree.save(os.path.join(app.config['UPLOAD_TEMPLET'],f"{bodyImgId+bodyImgId+bodyImgId+bodyImgId}.png"))
    final_saree = generetorFull.predict(saree)
    final_saree.save(os.path.join(app.config['UPLOAD_SAREE'],f"{bodyImgId+bodyImgId+bodyImgId+bodyImgId}.png"))
    img_io = BytesIO()
    final_saree.save(img_io, 'PNG')
    img_io.seek(0)
    img_base64 = base64.b64encode(img_io.read()).decode('utf-8')

    
    return jsonify({
        'border_file': border_file,
        'pallu_file': pallu_file,
        'pattern_file': pattern_file,
        'body_file': body_file,
        'final_templete': img_base64
    })
@app.route('/images', methods=['GET'])
def get_images():
    """Endpoint to list all uploaded images"""
    try:
        files = []
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            if allowed_file(filename):
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                files.append({
                    'filename': filename,
                    'filepath': filepath
                })
        
        return jsonify({
            'images': files,
            'count': len(files)
        })
    
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/image/<filename>', methods=['GET'])
def get_image(filename):
    """Endpoint to serve a specific image"""
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(filepath):
            return send_file(filepath)
        else:
            return jsonify({'error': 'Image not found'}), 404
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 