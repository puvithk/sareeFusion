import io
import json
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
UPLOAD_FOLDER = ''
UPLOAD_PARTS = 'upload_parts/'
UPLOAD_BODY = os.path.join(UPLOAD_PARTS , "body/")
UPLOAD_PALLU = os.path.join(UPLOAD_PARTS , "pallu/")
UPLOAD_BORDER = os.path.join(UPLOAD_PARTS , "border/")
UPLOAD_TEMPLET = 'templete/'
UPLOAD_SAREE = 'saree/'
VECTOR_SAREE = 'vector_saree/'
VECTOR_BORDER =  os.path.join(VECTOR_SAREE , "border/")
VECTOR_BODY = os.path.join(VECTOR_SAREE , "body/")
VECTOR_PALLU = os.path.join(VECTOR_SAREE , "pallu/")
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
dir_path = os.path.dirname(os.path.realpath(__file__))
# Create uploads directory if it doesn't exist
os.makedirs(os.path.join(dir_path,UPLOAD_FOLDER), exist_ok=True)
os.makedirs(os.path.join(dir_path,  UPLOAD_PARTS) , exist_ok=True)
os.makedirs(os.path.join(dir_path,  UPLOAD_BODY) , exist_ok=True)
os.makedirs(os.path.join(dir_path,  UPLOAD_PALLU) , exist_ok=True)
os.makedirs(os.path.join(dir_path,  UPLOAD_BORDER) , exist_ok=True)
os.makedirs(os.path.join(dir_path,UPLOAD_TEMPLET), exist_ok=True)
os.makedirs(os.path.join(dir_path,  UPLOAD_SAREE) , exist_ok=True)
os.makedirs(os.path.join(dir_path,  VECTOR_SAREE) , exist_ok=True)
os.makedirs(os.path.join(dir_path,  VECTOR_BORDER) , exist_ok=True)
os.makedirs(os.path.join(dir_path,  VECTOR_BODY) , exist_ok=True)
os.makedirs(os.path.join(dir_path,  VECTOR_PALLU) , exist_ok=True)
app.config['UPLOAD_FOLDER'] = os.path.join(dir_path,UPLOAD_FOLDER)
app.config['UPLOAD_PARTS'] =os.path.join(dir_path,  UPLOAD_PARTS)
app.config['UPLOAD_BODY'] =os.path.join(dir_path,  UPLOAD_BODY)
app.config['UPLOAD_PALLU'] =os.path.join(dir_path,  UPLOAD_PALLU)
app.config['UPLOAD_BORDER'] =os.path.join(dir_path,  UPLOAD_BORDER)
app.config['UPLOAD_TEMPLET'] = os.path.join(dir_path , UPLOAD_TEMPLET)
app.config['UPLOAD_SAREE'] = os.path.join(dir_path , UPLOAD_SAREE)
app.config['VECTOR_SAREE'] = os.path.join(dir_path , VECTOR_SAREE)
app.config['VECTOR_BORDER'] = os.path.join(dir_path , VECTOR_BORDER) 
app.config['VECTOR_BODY'] = os.path.join(dir_path , VECTOR_BODY)
app.config['VECTOR_PALLU'] = os.path.join(dir_path , VECTOR_PALLU)
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


@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    print(data)
    borderImgId = data['border']
    palluImgId = data['pallu']
    patternImgId = data['pattern']
    bodyImgId = data['body']
    prompt = data['prompt']
    print(prompt)
    if prompt is None:
        prompt = ""
    # Construct the folder paths
    border_folder = os.path.join(app.config['UPLOAD_PARTS'], f"{borderImgId}_parts")
    pallu_folder = os.path.join(app.config['UPLOAD_PARTS'], f"{palluImgId}_parts")
    pattern_folder = os.path.join(app.config['UPLOAD_PARTS'], f"{patternImgId}_parts")
    body_folder = os.path.join(app.config['UPLOAD_PARTS'], f"{bodyImgId}_parts")
    print(border_folder , pallu_folder , pattern_folder , body_folder)
    # Get the specific files
    border_file , pallu_file ,  body_file = None, None , None
    border_file = get_specific_file_in_folder(border_folder, "Border0")
    pallu_file = get_specific_file_in_folder(pallu_folder, "Pallu0")
    # pattern_file = get_specific_file_in_folder(pattern_folder, "Pattern0")
    body_file = get_specific_file_in_folder(body_folder, "Body0")
    print(border_file)
    print(pallu_file)
    print(body_file)
    if border_file is not None:
        border_image = Image.open(border_file).convert("RGB")
    if pallu_file is not None:
        pallu_image = Image.open(pallu_file).convert("RGB")
    if body_file is not None:
        body_image = Image.open(body_file).convert("RGB")
    else :
        body_image = None
    

    if body_image is not None:


        cropperd_border = cropCenter.crop_pre_region(border_image)
        # Resize so height=100, width is scaled to maintain aspect ratio
        target_height = 200
        aspect_ratio = cropperd_border.width / cropperd_border.height
        target_width = int(target_height * aspect_ratio)
        cropperd_border = cropperd_border.resize((target_width, target_height))
        
        saree =  generateSaree.tempelete(cropperd_border , pallu_image , body_image)
        print("Border file:", border_file)
        print("Pallu file:", pallu_file)
        print("Pattern file:", None) #pattern_file)
        print("Body file:", body_file)
        print("Final_templete" , saree)
        
        saree.save(os.path.join(app.config['UPLOAD_TEMPLET'],f"{bodyImgId+bodyImgId+bodyImgId+bodyImgId}.png"))
             
        print("Prompt " , prompt)

        final_saree = generetorFull.predict(saree,  prompt)
        final_saree.save(os.path.join(app.config['UPLOAD_SAREE'],f"{bodyImgId+bodyImgId+bodyImgId+bodyImgId}.png"))
    else :
        print("Only Prompt " , prompt)
        final_saree = generetorFull.predict(None,  prompt)
        final_saree.save(os.path.join(app.config['UPLOAD_SAREE'],f"{prompt[2]}.png"))
    img_io = BytesIO()
    final_saree.save(img_io, 'PNG')
    img_io.seek(0)
    img_base64 = base64.b64encode(img_io.read()).decode('utf-8')

    
    return jsonify({
        'border_file': border_file,
        'pallu_file': pallu_file,
        'pattern_file': None, #pattern_file,
        'body_file': body_file,
        'final_templete': img_base64
    })
@app.route('/images', methods=['GET'])
def get_images():
    """Endpoint to list all uploaded images as base64"""
    try:
        files = []
        
        for filename in os.listdir(app.config['UPLOAD_SAREE']):
            if allowed_file(filename):
                filepath = os.path.join(app.config['UPLOAD_SAREE'], filename)
                print(filepath)
                with open(filepath, "rb") as img_file:
                
                    img_bytes = img_file.read()
                    img_base64 = base64.b64encode(img_bytes).decode('utf-8')
                
                # Append data to response list
                files.append({
                    'image_id': filename.split("_")[0],
                    'filename': filename,
                    'base64': img_base64
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

@app.route('/saree/all')
def get_all_sarees():
    try:
        sarees = []
        for filename in os.listdir(app.config['UPLOAD_SAREE']):
            sarees.append({
                'filename': filename,
                'filepath': os.path.join(app.config['UPLOAD_SAREE'], filename)
            })
        return jsonify({
            'sarees': sarees,
            'count': len(sarees)
        })
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500


#This is the Updated part of the project 

@app.route("/upload_border" , methods=['POST'])
def process_upload_border():
    try:
    # Check if the post request has the file part
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file:
            # Generate a unique filename to avoid conflicts
            unique_filename = f"{uuid.uuid4().hex}.png"
            image = Image.open(io.BytesIO(file.read()))
            # Save the file
            border = generateSaree.get_border_processed(file=image)
            pattern = generetorFull.create_vector_border(border)
            image.save(os.path.join(app.config['UPLOAD_BORDER'] , unique_filename))
            pattern.save(os.path.join(app.config['UPLOAD_BORDER'] , "flat_graphic_" + unique_filename))
            images = generetorFull.remove_white_bg_cv2(pattern)
            print(os.path.join(app.config['VECTOR_BORDER']))
            images.save(os.path.join(app.config['VECTOR_BORDER'], unique_filename  ))
            return jsonify({"data" :unique_filename}) , 200
    except Exception as e:
        print(e)
        return jsonify({"Invalid" : str(e)}) , 506




@app.route("/upload_pallu" , methods=['POST'])
def process_upload_pallu():
    try:
    # Check if the post request has the file part
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
       
        # Generate a unique filename to avoid conflicts
        unique_filename = f"{uuid.uuid4().hex}.png"
        image = Image.open(io.BytesIO(file.read()))
        # Save the file
        border = generateSaree.get_border_processed(file=image)
        pattern = generetorFull.create_vector_pallu(border)
        image.save(os.path.join(app.config['UPLOAD_PALLU'] , unique_filename))
        pattern.save(os.path.join(app.config['UPLOAD_PALLU'] , "flat_graphic_" + unique_filename))
        images = generetorFull.remove_white_bg_cv2(pattern)
        print(os.path.join(app.config['VECTOR_PALLU']))
        images.save(os.path.join(app.config['VECTOR_PALLU'], unique_filename  ))
        return jsonify({"data" :unique_filename}) , 200
    except Exception as e:
        print(e)
        return jsonify({"Invalid" : str(e)}) , 506


@app.route("/upload_body" , methods=['POST'])
def process_upload_body():
    try:
    # Check if the post request has the file part
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file:
            # Generate a unique filename to avoid conflicts
            
            unique_filename = f"{uuid.uuid4().hex}.png"
            image = Image.open(io.BytesIO(file.read()))
            # Save the file
            border = generateSaree.get_border_processed(file=image)
            pattern = generetorFull.create_vector_body(border)
            image.save(os.path.join(app.config['UPLOAD_BODY'] , unique_filename))
            pattern.save(os.path.join(app.config['UPLOAD_BODY'] , "flat_graphic_" + unique_filename))
            images = generetorFull.remove_white_bg_cv2(pattern)
            print(os.path.join(app.config['VECTOR_BODY']))
            images.save(os.path.join(app.config['VECTOR_BODY'], unique_filename  ))
            return jsonify({"data" :unique_filename}) , 200
    except Exception as e:
        print(e)
        return jsonify({"Invalid" : str(e)}) , 506

@app.route('/get_border' , methods=['POST'])
def get_border():
    try :
        file_id =  request.form.get("file_id")
        image = Image.open(os.path.join(app.config['VECTOR_BORDER'] , file_id))
        buffer = BytesIO()
        
        image.save(buffer, format="PNG")
        buffer.seek(0)
        img_str = base64.b64encode(buffer.read()).decode("utf-8")
        return jsonify({
            "file" : img_str 
        }) , 200
    except Exception as e:
        return jsonify({
            "Error" : str(e)
        })

@app.route('/get_pallu' , methods=['POST'])
def get_pallu():
    try :
        file_id =  request.form.get("file_id")
        image = Image.open(os.path.join(app.config['VECTOR_PALLU'] , file_id))
        buffer = BytesIO()
        
        image.save(buffer, format="PNG")
        buffer.seek(0)
        img_str = base64.b64encode(buffer.read()).decode("utf-8")
        return jsonify({
            "file" : img_str 
        }) , 200
    except Exception as e:
        return jsonify({
            "Error" : str(e)
        })



@app.route('/get_body' , methods=['POST'])
def get_body():
    try :
        file_id =  request.form.get("file_id")
        image = Image.open(os.path.join(app.config['VECTOR_BODY'] , file_id))
        buffer = BytesIO()
        
        image.save(buffer, format="PNG")
        buffer.seek(0)
        img_str = base64.b64encode(buffer.read()).decode("utf-8")
        return jsonify({
            "file" : img_str 
        }) , 200
    except Exception as e:
        return jsonify({
            "Error" : str(e)
        })

@app.route("/generate-saree" ,   methods=['POST'])
def generate_saree():
    data = request.form
    border_id = data.get('border_id') 
    pallu_id = data.get('pallu_id')
    body_id = data.get('body_id')
    prompt = data.get("prompt")
    try :
        border_image = Image.open(os.path.join(app.config['VECTOR_BORDER'], border_id+'.png'  ))
        pallu_image = Image.open(os.path.join(app.config['VECTOR_PALLU'], pallu_id+'.png'  ))
        body_image = Image.open(os.path.join(app.config['VECTOR_BODY'], body_id+'.png'  ))
        templed_image = generateSaree.tempelete(border_image ,  pallu_image , body_image)
       
        saree_design = generetorFull.predict(image = templed_image,custom_prompt= prompt)
      
        buffer = BytesIO()
        templed_image.save(os.path.join(app.config['UPLOAD_TEMPLET'],f"{border_id + pallu_id + border_id}.png"))
        saree_design.save(os.path.join(app.config['UPLOAD_SAREE'],f"{border_id + pallu_id + border_id}.png"))
        saree_design.save(buffer, format="PNG")
        buffer.seek(0)
        img_str = base64.b64encode(buffer.read()).decode("utf-8")
        return jsonify({"file"  : img_str , 
                        "saree_id" : border_id + pallu_id + border_id} )
    except FileNotFoundError as fnf:
        return jsonify({"error":"File ID not found"}) , 302
    except Exception as e:
        print(e)
        return jsonify({"error"  : "Server error"}) , 503


@app.route('/generate-saree/<template_id>/<id>' , methods=['POST'])
def generate_saree_template(template_id , id ):
    try :
        data = request.get_json()   

        prompt = data.get("prompt")

        templed_image =  Image.open(os.path.join(app.config['UPLOAD_TEMPLET'],f"{template_id}.png"))
        saree_design = generetorFull.predict(image = templed_image, custom_prompt=prompt)
        buffer = BytesIO()
        saree_design.save(os.path.join(app.config['UPLOAD_SAREE'],f"{template_id}{id}.png"))
        saree_design.save(buffer, format="PNG")
        buffer.seek(0)
        img_str = base64.b64encode(buffer.read()).decode("utf-8")
        return jsonify({"file"  : img_str , 
                        "saree_id" : template_id+id} )        
    except FileNotFoundError as fnf:
        print(fnf)
        return jsonify({"Error" : "File not Found"})
    
    except Exception as e:
        return jsonify({"Error" : e}) , 504



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 