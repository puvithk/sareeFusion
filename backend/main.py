from h11._abnf import method
from asyncio import threads
import io
import json
import threading
from flask import Flask, request, jsonify, send_file , send_from_directory
from datetime import datetime, timezone

from flask_pymongo import PyMongo
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
import uuid
import cv2
from PIL import Image
from Genereating import new
from Proccessing.crop_image import CropCenter 
from Genereating.new import GenerateSaree 
from Genereating.generateSaree import GenerateComplete
from threading import Thread
from dotenv import load_dotenv
import base64
import random
from io import BytesIO
import boto3
from bson.objectid import ObjectId #
load_dotenv()
app = Flask(__name__, static_folder='frontend_build')

CORS(app, origins=["*"])
S3_BUCKET_NAME = 'sareefusion'
app.config['MONGO_URI'] =  os.environ.get('MONGO_URI')

mongo = PyMongo(app)
db = mongo.db

User = db.users
Assests = db.assests
Designs = db.designs
Combinations = db.combinations
# S3 PREFIXES (These act as folders)
UPLOAD_FOLDER = '' # The root of the bucket
UPLOAD_PARTS = 'upload_parts/'
UPLOAD_BODY = os.path.join(UPLOAD_PARTS , "body/")
UPLOAD_PALLU = os.path.join(UPLOAD_PARTS , "pallu/")
UPLOAD_BORDER = os.path.join(UPLOAD_PARTS , "border/")
UPLOAD_TEMPLET = 'templete/'
UPLOAD_SAREE = 'saree/'
VECTOR_SAREE = 'vector_saree/'
VECTOR_BORDER = os.path.join(VECTOR_SAREE , "border/")
VECTOR_BODY = os.path.join(VECTOR_SAREE , "body/")
VECTOR_PALLU = os.path.join(VECTOR_SAREE , "pallu/")

UPLOAD_BORDER = UPLOAD_BORDER if UPLOAD_BORDER.endswith('/') else UPLOAD_BORDER + '/'
VECTOR_BORDER = VECTOR_BORDER if VECTOR_BORDER.endswith('/') else VECTOR_BORDER + '/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
cropCenter = CropCenter()
generateSaree = GenerateSaree()
generetorFull = GenerateComplete()
def allowed_file(filename):
    """Check if the file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

import os

try:
    s3 = boto3.client('s3')
    print("S3 client initialized successfully.")
except Exception as e:
    print(f"Error initializing S3 client: {e}")
    s3 = None

def upload_in_memory_image(img_object, key):
    """Saves PIL Image to a buffer and uploads the buffer to S3."""
    global s3, S3_BUCKET_NAME
    if not s3:
        raise Exception("S3 client is not initialized.")
    buffer = BytesIO()
    img_object.save(buffer, format='PNG') 
    buffer.seek(0)
    

    s3.upload_fileobj(buffer, S3_BUCKET_NAME, key ,
    ExtraArgs={
            'ContentType': 'image/png',      
            'ContentDisposition': 'inline'    
        })


def get_image_from_s3(key):
    global s3, S3_BUCKET_NAME
    if not s3:
        raise Exception("S3 client is not initialized.")
    try:
        buffer = BytesIO()
        s3.download_fileobj(S3_BUCKET_NAME, key, buffer)
        buffer.seek(0)
        return Image.open(buffer)
    except Exception as e:
        print(f"Error retrieving image from S3: {e}")
        return None

def get_image_from_s3_as_link(key):
    global s3, S3_BUCKET_NAME
    if not s3:
        raise Exception("S3 client is not initialized.")
    try:
        url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET_NAME, 'Key': key},
            ExpiresIn=1800  
        )
        return url
    except Exception as e:
        print(f"Error retrieving image from S3: {e}")
        return None
# --- 1. Health Check Endpoint ---
# Purpose: Verify Flask is running.
aspect_ratio = get_image_from_s3("reference image/reference_image.png")

def get_saree_description(design_id, image_bytes, user_id):

    try:
        # Call your Gemini-based generator
        result = generetorFull.get_description_title(image_bytes)
        
        # Prepare the fields to update
        update_fields = {
            "title": result.get("title"),
            "description": result.get("description"),
            "tags": result.get("tags"),
            "updated_at": datetime.now(timezone.utc)
        }

        # Update MongoDB document
        Designs.update_one(
            {"design_id": design_id},
            {"$set": update_fields}
        )
        print(f"Design {design_id} updated with Gemini metadata.")
    except Exception as e:
        print(f"Failed to get description for design {design_id}: {e}")


def is_border_available(border_id):
    try:
        border = Assests.find_one({'uuid_name': border_id , "asset_type" : "border"})

        if border is None:
            return False
        return True
    except Exception as e:
        print(f"Error checking border availability: {e}")
        return False

def is_body_available(body_id):
    try:
        body = Assests.find_one({'uuid_name': body_id , "asset_type" : "body"})

        if body is None:
            return False
        return True
    except Exception as e:
        print(f"Error checking body availability: {e}")
        return False

def is_pallu_available(pallu_id):
    try:
        pallu = Assests.find_one({'uuid_name': pallu_id , "asset_type" : "pallu"})

        if pallu is None:
            return False
        return True
    except Exception as e:
        print(f"Error checking pallu availability: {e}")
        return False    

@app.route('/health', methods=['GET'])
def health_check():
    """Simple endpoint to verify the API is running."""
    return jsonify({
        "status": "ok",
        "service": "SareeFusion API"
    }), 200

# --- 2. S3 Configuration Test Endpoint ---
# Purpose: Verify Boto3 can communicate with your bucket.
@app.route('/test-s3', methods=['GET'])
def test_s3_connection():
    """Attempts to list the top 5 objects in the configured S3 bucket."""
    if not s3:
        return jsonify({"error": "S3 client not initialized. Check credentials and region."}), 500
        
    try:
        # Use the 'list_objects_v2' API call, which requires the s3:ListBucket permission
        response = s3.list_objects_v2(
            Bucket=S3_BUCKET_NAME,
            MaxKeys=5  # Only fetch a few objects to test
        )
        
        # Extract file keys if objects exist
        contents = [item['Key'] for item in response.get('Contents', [])]
        
        return jsonify({
            "status": "success",
            "message": f"Successfully connected to S3 bucket '{S3_BUCKET_NAME}'.",
            "top_files_listed": contents,
            "file_count_in_response": len(contents)
        }), 200
        
    except s3.exceptions.NoSuchBucket:
        return jsonify({"error": f"The bucket '{S3_BUCKET_NAME}' does not exist or you don't have access."}), 404
    except Exception as e:
        # This will catch permissions errors (403 Forbidden), invalid credentials, etc.
        return jsonify({"error": f"S3 connection failed. Check IAM policy and environment keys. Details: {str(e)}"}), 500

def allowed_file(filename):
    """Check if the file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS




@app.route('/get_user' , methods=['POST'])
def get_user():
    data = request.form
    user_name = data.get("username")
    user = User.find_one({
        'username' : user_name
    })
    if user:
        # Convert ObjectId to string for JSON compatibility
        user['_id'] = str(user['_id'])
        return jsonify(user), 200
    else:
        return jsonify({"error": "User not found"}), 406
    



@app.route("/upload_border" , methods=['POST'])
def process_upload_border():
    try:
    # Check if the post request has the file part
        data = request.form
        user_id = data.get('id')
   
        user =  User.find_one({"_id": ObjectId(user_id)})

        if user is None :
            return jsonify({'error ' : "Not Allowed"}) , 405
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
  
        # Generate a unique filename to avoid conflicts
        filename = secure_filename(file.filename)
        uuid_filename = f"{uuid.uuid4().hex}"
        unique_filename = f"{uuid_filename}.png"
       
        image = Image.open(io.BytesIO(file.read()))
 
    
        KEY_UPLOAD_BORDER = UPLOAD_BORDER + unique_filename
        KEY_UPLOAD_FLAT = UPLOAD_BORDER + "flat_graphic_" + unique_filename
        KEY_VECTOR_BORDER = VECTOR_BORDER + unique_filename            # Save the file
        border = generateSaree.get_border_processed(file=image)
        pattern = generetorFull.create_vector_border(border)
        images_without_bg = generetorFull.remove_white_bg_cv2(pattern)
        upload_in_memory_image(border , KEY_UPLOAD_BORDER)
        upload_in_memory_image(pattern , KEY_UPLOAD_FLAT)
        upload_in_memory_image(images_without_bg , KEY_VECTOR_BORDER)
        new_assets = {
            "uuid_name" : uuid_filename,
            "user" :user,
            "asset_type" : "border",
            "original_s3_key" : KEY_UPLOAD_BORDER,
            "vector_s3_key":KEY_VECTOR_BORDER
        }
        Assests.insert_one(new_assets)
        return jsonify({"data" :uuid_filename ,
            's3_key_vector' : KEY_VECTOR_BORDER,
            "uuid_name": new_assets.get('uuid_name')}) , 200
    except Exception as e:
        print(e)
        return jsonify({"Invalid" : str(e)}) , 506



@app.route("/upload_pallu" , methods=['POST'])
def process_upload_pallu():
    try:
    # Check if the post request has the file part
        data = request.form
        user_id = data.get('id')
   
        user =  User.find_one({"_id": ObjectId(user_id)})

        if user is None :
            return jsonify({'error ' : "Not Allowed"}) , 405
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file:
            # Generate a unique filename to avoid conflicts
            filename = secure_filename(file.filename)
            uuid_filename = f"{uuid.uuid4().hex}"
            unique_filename = f"{uuid_filename}.png"
            KEY_UPLOAD_PALLU = UPLOAD_PALLU +  unique_filename
            KEY_UPLOAD_PALLU_VECTOR = UPLOAD_PALLU + 'flat_vector_'+unique_filename
            KEY_VECTOR_PALLU =  VECTOR_PALLU + unique_filename
            image = Image.open(io.BytesIO(file.read()))
            # Save the file
            pallu = generateSaree.get_border_processed(file=image)
            pattern = generetorFull.create_vector_pallu(pallu)
            images = generetorFull.remove_white_bg_cv2(pattern)
            upload_in_memory_image(pallu ,KEY_UPLOAD_PALLU )
            upload_in_memory_image(pattern  , KEY_UPLOAD_PALLU_VECTOR)
            upload_in_memory_image(images , KEY_VECTOR_PALLU)
            new_assets = {
            "uuid_name" : uuid_filename,
            "user" :user,
            "asset_type" : "pallu",
            "original_s3_key" : KEY_UPLOAD_PALLU,
            "vector_s3_key":KEY_VECTOR_PALLU
            }
            Assests.insert_one(new_assets)
            return jsonify({"data" :uuid_filename,
            "pallu_id" : KEY_VECTOR_PALLU,
            "uuid_name": new_assets.get('uuid_name')}) , 200
    except Exception as e:
        print(e)
        return jsonify({"Invalid" : str(e)}) , 506


@app.route("/upload_body" , methods=['POST'])
def process_upload_body():
    try:
    # Check if the post request has the file part
        data = request.form
        user_id = data.get('id')
   
        user =  User.find_one({"_id": ObjectId(user_id)})

        if user is None :
            return jsonify({'error ' : "Not Allowed"}) , 405
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file:
            # Generate a unique filename to avoid conflicts
            filename = secure_filename(file.filename)
            uuid_filename = f"{uuid.uuid4().hex}"
            unique_filename = f"{uuid_filename}.png"
            KEY_UPLOAD_BODY = UPLOAD_BODY +  unique_filename
            KEY_UPLOAD_BODY_VECTOR = UPLOAD_BODY + 'flat_vector_'+unique_filename
            KEY_VECTOR_BODY=  VECTOR_BODY + unique_filename
           
           
            image = Image.open(io.BytesIO(file.read()))
            # Save the file
            body = generateSaree.get_border_processed(file=image)
            pattern = generetorFull.create_vector_body(body)
            
            images = generetorFull.remove_white_bg_cv2(pattern)
            upload_in_memory_image(body ,KEY_UPLOAD_BODY)
            upload_in_memory_image(pattern, KEY_UPLOAD_BODY_VECTOR)
            upload_in_memory_image(images , KEY_VECTOR_BODY)
            new_assets = {
            "uuid_name" : uuid_filename,
            "user" :user,
            "asset_type" : "body",
            "original_s3_key" : KEY_UPLOAD_BODY,
            "vector_s3_key":KEY_VECTOR_BODY
            }
            Assests.insert_one(new_assets)
            return jsonify({"data" :uuid_filename ,
            'file_id' : KEY_VECTOR_BODY ,
            "uuid_name": new_assets.get('uuid_name')}) , 200
    except Exception as e:
        print(e)
        return jsonify({"Invalid" : str(e)}) , 506

@app.route('/get_border' , methods=['POST'])
def get_border():
    try :
        file_id =  request.form.get("file_id")
        if file_id is None:
            return jsonify({"Error" : "Not found"})
        s3_key = VECTOR_BORDER +  file_id+ '.png'
        url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET_NAME, 'Key': s3_key},
            ExpiresIn=1800  
        )
        
        return jsonify({
            "file_url" : url 
        }) , 200
        
    except Exception as e:
        return jsonify({
            "Error" : str(e)
        }) , 500
        
@app.route('/get_pallu' , methods=['POST'])
def get_pallu():
    try :
        file_id =  request.form.get("file_id")
        if file_id is None:
            return jsonify({"Error" : "Not found"})
        s3_key = VECTOR_PALLU +  file_id+'.png'
        url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET_NAME, 'Key': s3_key},
            ExpiresIn=1800  
        )
        
        return jsonify({
            "file_url" : url 
        }) , 200
        
    except Exception as e:
        return jsonify({
            "Error" : str(e)
        }) , 500
        


@app.route('/get_body' , methods=['POST'])
def get_body():
    try :
        file_id =  request.form.get("file_id")
        if file_id is None:
            return jsonify({"Error" : "Not found"})
        s3_key = VECTOR_BODY +  file_id+'.png'
        url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET_NAME, 'Key': s3_key},
            ExpiresIn=1800  
        )
        
        return jsonify({
            "file_url" : url 
        }) , 200
        
    except Exception as e:
        return jsonify({
            "Error" : str(e)
        }) , 500


@app.route("/generate-saree" ,   methods=['POST'])
def generate_saree():
    data = request.form
    border_id = data.get('border_id') 
    pallu_id = data.get('pallu_id')
    body_id = data.get('body_id')
    prompt = data.get("prompt")
    user_id = data.get('id')
   
    user =  User.find_one({"_id": ObjectId(user_id)})

    if user is None :
        return jsonify({'error ' : "Not Allowed"}) , 405

    try :
        border_filename = VECTOR_BORDER + border_id  + ".png"
        pallu_filename = VECTOR_PALLU + pallu_id  + ".png"
        body_filename = VECTOR_BODY + body_id  + ".png"
        border_image = get_image_from_s3(border_filename)
        pallu_image =get_image_from_s3(pallu_filename)
        body_image = get_image_from_s3(body_filename)
        templed_image = generateSaree.tempelete(border_image ,  pallu_image , body_image)
       
        saree_design = generetorFull.predict(image = templed_image,custom_prompt= prompt , accept_ration=aspect_ratio)
        if saree_design is None:
            return jsonify({
                "Error" : "Server could not process"
            }) , 504
        KEY_TEMPLETE =  UPLOAD_TEMPLET + f'{border_id+ pallu_id+body_id}.png'
        KEY_SAREE = UPLOAD_SAREE + f'{border_id+ pallu_id+body_id}.png'
        buffer = BytesIO()
        print(KEY_SAREE , KEY_TEMPLETE)
        upload_in_memory_image(saree_design ,KEY_SAREE )
        upload_in_memory_image(templed_image , KEY_TEMPLETE)
        saree_design.save(buffer, format="PNG")
        buffer.seek(0)
        img_str = base64.b64encode(buffer.read()).decode("utf-8")
        image_bytes = buffer.getvalue()
        new_design = {
            "design_id" : str(uuid.uuid4()),
            "design_s3_key" : KEY_SAREE,
            "templete_s3_key" : KEY_TEMPLETE,
             "border_id" : border_id ,
            "pallu_id" : pallu_id,
            "body_id":body_id,
            "created_at" : datetime.now(timezone.utc),
            "user" : user
        }
        Designs.insert_one(new_design)
        thread = threading.Thread(
            target=get_saree_description,
            args=(new_design["design_id"], image_bytes, user),
            daemon=True  # optional, so thread dies when main process exits
        )
        thread.start()
        return jsonify({"file"  : img_str , 
                        "saree_id" : border_id + pallu_id + body_id ,
                        "id" : new_design.get('design_id')}) ,200
    except FileNotFoundError as fnf:
        return jsonify({"error":"File ID not found"}) , 302
    except Exception as e:
        print(e)
        return jsonify({"error"  : "Server error"}) , 503


@app.route('/get_saree' , methods=['POST'])
def get_saree():
    try:
        saree_id =  request.form.get('saree_id')
        s3_key = UPLOAD_SAREE + saree_id + ".png"
        url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET_NAME, 'Key': s3_key},
            ExpiresIn=1800  
        )
        
        return jsonify({
            "file_url" : url 
        }) , 200
    except Exception as e:
    # --- SHOW THE ERROR ---
        print(f"Error generating URL: {e}") 
        return jsonify({"error": str(e)}), 500 



@app.route('/generate-saree/<id>' , methods=['POST'])
def generate_saree_template( id ):
    try :
        data = request.form   
     
        prompt = data.get("prompt")
        user_id = data.get('id')
        template_id = data.get("templete_id")
        user =  User.find_one({"_id": ObjectId(user_id)})
        prev = None
        templed_image = None
        border_image = None
        pallu_image = None
        body_image = None
        previous_image = None

        if template_id :
            prev = Designs.find_one({
                "templete_s3_key" : UPLOAD_TEMPLET + template_id +'.png'
            })
        else :
            templed_image = None
        if user is None :
            return jsonify({'error ' : "Not Allowed"}) , 405
        saree_one = Designs.find_one({
            'design_s3_key' : UPLOAD_SAREE + template_id + '.png'
        })
        if int(id) == 1 :
            previous_image =  get_image_from_s3(UPLOAD_SAREE + template_id + '.png')
        else :
            previous_image =  get_image_from_s3(UPLOAD_SAREE + template_id + f'{int(id)-1}.png')
        if prev:
            templed_image =  get_image_from_s3(UPLOAD_TEMPLET + template_id + '.png')
        if saree_one.get('border_id'):
            border_image = get_image_from_s3(UPLOAD_BORDER + saree_one.get('border_id') + '.png' )
        if saree_one.get('pallu_id'):
            pallu_image = get_image_from_s3(UPLOAD_PALLU + saree_one.get('pallu_id') + '.png' )

        if saree_one.get('body_id'):
            body_image = get_image_from_s3(UPLOAD_BODY + saree_one.get('body_id') + '.png' )

 


        saree_design = generetorFull.predict_image_old(image = templed_image, custom_prompt=prompt , old_image=previous_image , aspect_ratio=aspect_ratio ,image_extra = [i for i in [border_image, body_image, pallu_image] if i])
        if saree_design  is None:
            return jsonify({
                "Error" : "Internal Error" 
            }) , 500
        buffer = BytesIO()
        upload_in_memory_image(saree_design ,  UPLOAD_SAREE + template_id + id  + '.png')
        saree_design.save(buffer, format="PNG")
        buffer.seek(0)
        img_str = base64.b64encode(buffer.read()).decode("utf-8")
        new_design = {
            "design_id": str(uuid.uuid4()),
            "design_s3_key": UPLOAD_SAREE + template_id + id + '.png',
            "templete_s3_key": template_id,
              "border_id": prev.get('border_id') if prev else None,
    "pallu_id": prev.get('pallu_id') if prev else None,
    "body_id": prev.get('body_id') if prev else None,
            "created_at": datetime.now(timezone.utc),
            "user": user
        }
        Designs.insert_one(new_design)
        image_bytes = buffer.getvalue()
        thread = threading.Thread(
            target=get_saree_description,
            args=(new_design["design_id"], image_bytes, user),
            daemon=True  # optional, so thread dies when main process exits
        )
        thread.start()
        return jsonify({"file"  : img_str , 
                        "saree_id" : template_id+id ,
                        'design_id' : new_design.get('design_id')} )        
    except FileNotFoundError as fnf:
        print(fnf)
        return jsonify({"Error" : "File not Found"})
    
    except Exception as e:
        return jsonify({"Error" : e}) , 504



@app.route("/generate-saree-image" ,   methods=['POST'])
def generate_saree_image():
    data = request.form
    border_id = data.get('border_id') 
    pallu_id = data.get('pallu_id')
    body_id = data.get('body_id')
    prompt = data.get("prompt")
    user_id = data.get('id')
   
    user =  User.find_one({"_id": ObjectId(user_id)})

    if user is None :
        return jsonify({'error ' : "Not Allowed"}) , 405

    try :
        body_image = None
        border_image = None
        pallu_image = None
        if border_id:
            border_filename = VECTOR_BORDER + border_id  + ".png"
            border_image = get_image_from_s3(border_filename)
        if pallu_id:
            pallu_filename = VECTOR_PALLU + pallu_id  + ".png"
            pallu_image =get_image_from_s3(pallu_filename)
        if body_id:
            body_filename = VECTOR_BODY + body_id  + ".png"
            body_image = get_image_from_s3(body_filename)
        saree_design = generetorFull.predict_image(saree_border=border_image , saree_body=body_image , saree_pallu=pallu_image , custom_prompt=prompt, aspect_ratio = aspect_ratio)
        if saree_design is None:
            return jsonify({
                "Error" : "Server could not process"
            }) , 504
        KEY_TEMPLETE =  UPLOAD_TEMPLET + f'{border_id+ pallu_id+body_id}.png'
        KEY_SAREE = UPLOAD_SAREE + f'{border_id+ pallu_id+body_id}.png'
        buffer = BytesIO()
        print(KEY_SAREE , KEY_TEMPLETE)
        upload_in_memory_image(saree_design ,KEY_SAREE )
        
        saree_design.save(buffer, format="PNG")
        buffer.seek(0)
        img_str = base64.b64encode(buffer.read()).decode("utf-8")
        new_design = {
            "design_id" : str(uuid.uuid4()),
            "design_s3_key" : KEY_SAREE,
            "templete_s3_key" : None,
            "border_id" : border_id ,
            "pallu_id" : pallu_id,
            "body_id":body_id,
            "created_at" : datetime.now(timezone.utc),
            "user" : user
        }
        Designs.insert_one(new_design)
        image_bytes = buffer.getvalue()
        thread = threading.Thread(
            target=get_saree_description,
            args=(new_design["design_id"], image_bytes, user),
            daemon=True  # optional, so thread dies when main process exits
        )
        thread.start()
        return jsonify({"file"  : img_str , 
                        "saree_id" : border_id + pallu_id + body_id } ) , 200
    except FileNotFoundError as fnf:
        return jsonify({"error":"File ID not found"}) , 302
    except Exception as e:
        print(e)
        return jsonify({"error"  : "Server error"}) , 503

@app.route("/generate-saree-image/<id>" ,   methods=['POST'])
def generate_saree_image_id(id):
    data = request.form
    border_id = data.get('border_id') 
    pallu_id = data.get('pallu_id')
    body_id = data.get('body_id')
    prompt = data.get("prompt")
    user_id = data.get('id')
   
    user =  User.find_one({"_id": ObjectId(user_id)})

    if user is None :
        return jsonify({'error ' : "Not Allowed"}) , 405

    try :
        border_filename = VECTOR_BORDER + border_id  + ".png"
        pallu_filename = VECTOR_PALLU + pallu_id  + ".png"
        body_filename = VECTOR_BODY + body_id  + ".png"
        border_image = get_image_from_s3(border_filename)
        pallu_image =get_image_from_s3(pallu_filename)
        body_image = get_image_from_s3(body_filename)
        saree_design = generetorFull.predict_image(saree_border=border_image , saree_body=body_image , saree_pallu=pallu_image , custom_prompt=prompt)
        if saree_design is None:
            return jsonify({
                "Error" : "Server could not process"
            }) , 504
        KEY_TEMPLETE =  UPLOAD_TEMPLET + f'{border_id+ pallu_id+body_id}{id}.png'
        KEY_SAREE = UPLOAD_SAREE + f'{border_id+ pallu_id+body_id}{id}.png'
        buffer = BytesIO()
        print(KEY_SAREE , KEY_TEMPLETE)
        upload_in_memory_image(saree_design ,KEY_SAREE )    
        
        saree_design.save(buffer, format="PNG")
        buffer.seek(0)
        img_str = base64.b64encode(buffer.read()).decode("utf-8")
        new_design = {
            "design_id" : str(uuid.uuid4()),
            "design_s3_key" : KEY_SAREE,
            "templete_s3_key" : None,
            "border_id" : border_id ,
            "pallu_id" : pallu_id,
            "body_id":body_id,
            "created_at" : datetime.now(timezone.utc),
            "user" : user
        }
        Designs.insert_one(new_design)
        
        image_bytes = buffer.getvalue()
        thread = threading.Thread(
            target=get_saree_description,
            args=(new_design["design_id"], image_bytes, user),
            daemon=True  # optional, so thread dies when main process exits
        )
        thread.start()
        return jsonify({"file"  : img_str , 
                        "saree_id" : border_id + pallu_id + body_id + f'{id}' ,
                        "design_id" : new_design.get("design_id")} ) , 200
    except FileNotFoundError as fnf:
        return jsonify({"error":"File ID not found"}) , 302
    except Exception as e:
        print(e)
        return jsonify({"error"  : "Server error"}) , 503


@app.route("/get_all_saree/<id>", methods=['POST'])
def get_saree_of_user(id):
    try:
        user_id = request.form.get("id")
        page = int(id)  # Get page number, default to 1
        limit = 4 # Number of images per page

        user = User.find_one({'_id': ObjectId(user_id)})
        if user is None:
            return jsonify({"Error": "Not allowed"}), 405

        skip_count = (page - 1) * limit  # Calculate how many documents to skip

        sarees = Designs.find({
            "user._id": user["_id"]
        }).sort("created_at", -1).skip(skip_count).limit(limit)

        lastest_design = []
      
        for saree in sarees:
           
            lastest_design.append({
                'id': str(saree.get('_id', None)),
                'design_id': saree.get('design_id', None),
                'border_id': saree.get('border_id', None),
                'pallu_id': saree.get('pallu_id', None),
                'body_id': saree.get('body_id', None),
                'description': saree.get('description', None),
                'tag': saree.get('tags', None),
                'title': saree.get('title', None),
                'src': s3.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': S3_BUCKET_NAME, 'Key': saree.get('design_s3_key', '')},
                    ExpiresIn=1800
                )
            })
      
        return jsonify({'data': lastest_design})

    except Exception as e:
        print(e)
        return jsonify({'error': "Server error: " + str(e)}), 503





#|-------------------------------------------------------------------------------------|
#|                                                                                     |
#|                                                                                     |
#|                  Latest Updates for meeting in 05/02/2026                           |
#|                                                                                     |
#|                                                                                     |
#|-------------------------------------------------------------------------------------|


#Funtion used to upload border image 
@app.route('/api/saree/borders/upload' , methods=['POST'])
def create_border():
    """Funtion used to upload border image 
     Endpoint : /api/saree/borders/upload
     Function name : create_border
     Method : POST
     Data : user_id as id , image 
     return : 
      405 if user not found ,
      400 if no image provided , 
      400 if no file selected ,
      200 if success,
      503 if server error
    On success returns : 
    {
        "data" : border_image as link,
        "s3_key_border" : KEY_UPLOAD_BORDER,
        "uuid_name" : #Border uuid name
    }
    """
    try:
        # Check if the post request has the file part
        data = request.form
        user_id = data.get('id')
        #Find user by id
        user =  User.find_one({"_id": ObjectId(user_id)})
        if user is None :
            #User not found
            return jsonify({'error ' : "Not Allowed"}) , 405
        
        #Check if image is provided
        if 'image' not in request.files:
            #Image not found 
            return jsonify({'error': "No image file provided"}), 400
        file = request.files['image']
        #Check if file is selected
        if file.filename == '':
            #File is empty 
            return jsonify({'error': "No file selected"}), 400
        # Generate a unique filename to avoid conflicts
        filename = secure_filename(file.filename)
        uuid_filename = f"{uuid.uuid4().hex}"
        unique_filename = f"{uuid_filename}.png"
        image = Image.open(io.BytesIO(file.read()))
        #KEY for border image in S3
        KEY_UPLOAD_BORDER = UPLOAD_BORDER + unique_filename           # Save the file
        border = generateSaree.get_border_processed(file=image)
        #Upload border image to S3
        try:
            #Upload border image to S3
            upload_in_memory_image(border , KEY_UPLOAD_BORDER)
        except Exception as e:
            print(e)
            #Failed updation of border image
            return jsonify({'error': "Server error: " + str(e)}), 503
        #Create new asset
        new_assets = {
            "uuid_name" : uuid_filename,
            "user" :user,
            "asset_type" : "border",
            "original_s3_key" : KEY_UPLOAD_BORDER,
        }
        #Insert new asset
        try:
            Assests.insert_one(new_assets)
        except Exception as e:
            print(e)
            #Failed updation of border assests
            return jsonify({'error': "Border assests cannot be created " + str(e)}), 503
        try :
            image_url =  get_image_from_s3_as_link(KEY_UPLOAD_BORDER)
        except:
            image_url = None
            return jsonify({'error': "Unable to save image"}), 503
        return jsonify(
            {"data" :image_url ,
            's3_key_border' : KEY_UPLOAD_BORDER,
            "uuid_name": new_assets.get('uuid_name')}
            ) , 200
    except Exception as e:
        print(e)
        return jsonify({'error': "Server error: " + str(e)}), 503
#Get border by id
@app.route('/api/saree/borders/<id>' , methods=['GET'])
def get_border_by_id(id):
    """Funtion used to get border image 
     Endpoint : /api/saree/borders/<id>
     Function name : get_border_by_id
     Method : GET
     Data : id
     return : 
      404 if border not found,
      503 if server error
    On success returns : 
    {
        "data" : border_image as link
    }
    """
    try:
        #Find border by id
        border = Assests.find_one({'uuid_name': id , "asset_type" : "border"})

        if border is None:
            #Border not found
            return jsonify({'error': 'Border not found'}), 404
        
        #Get border image from s3
        border_image = get_image_from_s3_as_link(border.get('original_s3_key'))
        return jsonify({'data': border_image}) , 200
    except Exception as e:
        print(e)
        return jsonify({'error': "Server error: " + str(e)}), 503

#Funtion used to upload pallu image 
@app.route('/api/saree/pallu/upload' , methods=['POST'])
def create_pallu():
    """Funtion used to upload pallu image 
     Endpoint : /api/saree/pallu/upload
     Function name : create_pallu
     Method : POST
     Data : user_id as id , image 
     return : 
      405 if user not found ,
      400 if no image provided , 
      400 if no file selected ,
      200 if success,
      503 if server error
    On success returns : 
    {
        "data" : pallu_image as link,
        "s3_key_pallu" : KEY_UPLOAD_PALLU,
        "uuid_name" : Pallu uuid name
    }
    """
    try:
        # Check if the post request has the file part
        data = request.form
        user_id = data.get('id')
        #Find user by id
        user =  User.find_one({"_id": ObjectId(user_id)})
        if user is None :
            #User not found
            return jsonify({'error ' : "Not Allowed"}) , 405
        if 'image' not in request.files:
            #Image not found 
            return jsonify({'error': 'No image file provided'}), 400
        file = request.files['image']
        if file.filename == '':
            #File is empty 
            return jsonify({'error': 'No file selected'}), 400
        # Generate a unique filename to avoid conflicts
        filename = secure_filename(file.filename)
        uuid_filename = f"{uuid.uuid4().hex}"
        unique_filename = f"{uuid_filename}.png"
        image = Image.open(io.BytesIO(file.read()))
        KEY_UPLOAD_PALLU = UPLOAD_PALLU + unique_filename           # Save the file
        pallu = generateSaree.get_border_processed(file=image)
        upload_in_memory_image(pallu , KEY_UPLOAD_PALLU)
        new_assets = {
            "uuid_name" : uuid_filename,
            "user" :user,
            "asset_type" : "pallu",
            "original_s3_key" : KEY_UPLOAD_PALLU,
        }
        Assests.insert_one(new_assets)
        try :
            image_url =  get_image_from_s3_as_link(KEY_UPLOAD_PALLU)
        except:
            image_url = None
            return jsonify({'error': "Unable to save image"}), 503
        return jsonify({"data" :image_url ,
            's3_key_pallu' : KEY_UPLOAD_PALLU,
            "uuid_name": new_assets.get('uuid_name')}) , 200
    except Exception as e:
        print(e)
        return jsonify({'error': "Server error: " + str(e)}), 503

#Get pallu by id
@app.route('/api/saree/pallu/<id>' , methods=['GET'])
def get_pallu_by_id(id):
    """Funtion used to get pallu image 
     Endpoint : /api/saree/pallu/<id>
     Function name : get_pallu_by_id
     Method : GET
     Data : id
     return : 
      404 if pallu not found,
      503 if server error
    On success returns : 
    {
        "data" : pallu_image as link
    }
    """
    try:
        pallu = Assests.find_one({'uuid_name': id , "asset_type" : "pallu"})

        if pallu is None:
            #Pallu not found
            return jsonify({'error': 'Pallu not found'}), 404
        pallu_image = get_image_from_s3_as_link(pallu.get('original_s3_key'))
        return jsonify({'data': pallu_image}) , 200
    except Exception as e:
        print(e)
        return jsonify({'error': "Server error: " + str(e)}), 503

#Funtion used to upload body image 
@app.route("/api/saree/body/upload" , methods=['POST'])
def create_body():
    """Funtion used to upload body image 
     Endpoint : /api/saree/body/upload
     Function name : create_body
     Method : POST
     Data : user_id as id , image 
     return : 
      405 if user not found ,
      400 if no image provided , 
      400 if no file selected ,
      200 if success,
      503 if server error
    On success returns : 
    {
        "data" : body_image as link,
        "s3_key_body" : KEY_UPLOAD_BODY,
        "uuid_name" : Body uuid name
    }
    """
    try:
        # Check if the post request has the file part
        data = request.form
        user_id = data.get('id')
        #Find user by id
        user =  User.find_one({"_id": ObjectId(user_id)})
        if user is None :
            #User not found
            return jsonify({'error ' : "Not Allowed"}) , 405
        if 'image' not in request.files:
            #Image not found 
            return jsonify({'error': 'No image file provided'}), 400
        file = request.files['image']
        if file.filename == '':
            #File is empty 
            return jsonify({'error': 'No file selected'}), 400
        # Generate a unique filename to avoid conflicts
        filename = secure_filename(file.filename)
        uuid_filename = f"{uuid.uuid4().hex}"
        unique_filename = f"{uuid_filename}.png"
        image = Image.open(io.BytesIO(file.read()))
        #Creating key for body image for s3
        KEY_UPLOAD_BODY = UPLOAD_BODY + unique_filename           # Save the file
        #Processing body image
        body = generateSaree.get_border_processed(file=image)
        try:
            #Uploading body image to s3
            upload_in_memory_image(body , KEY_UPLOAD_BODY)
        except Exception as e:
            print(e)
            return jsonify({'error': "Server error: " + str(e)}), 503
        new_assets = {
            "uuid_name" : uuid_filename,
            "user" :user,
            "asset_type" : "body",
            "original_s3_key" : KEY_UPLOAD_BODY,
        }
        try:
            #Inserting body image to database
            Assests.insert_one(new_assets)
        except Exception as e:
            print(e)
            return jsonify({'error': "Server error: " + str(e)}), 503
        try :
            image_url =  get_image_from_s3_as_link(KEY_UPLOAD_BODY)
        except:
            image_url = None
            return jsonify({'error': "Unable to save image"}), 503
        return jsonify({"data" :image_url ,
            's3_key_body' : KEY_UPLOAD_BODY,
            "uuid_name": new_assets.get('uuid_name')}) , 200
    except Exception as e:
        print(e)
        return jsonify({'error': "Server error: " + str(e)}), 503
#Get body by id
@app.route('/api/saree/body/<id>' , methods=['GET'])
def get_body_by_id(id):
    """Funtion used to get body image 
     Endpoint : /api/saree/body/<id>
     Function name : get_body_by_id
     Method : GET
     Data : id
     return : 
      404 if body not found,
      503 if server error
    On success returns : 
    {
        "data" : body_image as link
    }
    """
    try:
        body = Assests.find_one({'uuid_name': id , "asset_type" : "body"})

        if body is None:
            return jsonify({'error': 'Body not found'}), 404
        body_image = get_image_from_s3_as_link(body.get('original_s3_key'))
        return jsonify({'data': body_image}) , 200
    except Exception as e:
        print(e)
        return jsonify({'error': "Server error: " + str(e)}), 503


#Get saree by id
@app.route("/api/saree/<id>" , methods=['GET'])
def get_saree_by_id(id):
    """Funtion used to get saree image 
     Endpoint : /api/saree/<id>
     Function name : get_saree_by_id
     Method : GET
     Data : id
     return : 
      404 if saree not found,
      503 if server error
    On success returns : 
    {
        "data" : saree_image as link
    }
    """
    try:
        saree = Designs.find_one({'design_id': id })

        if saree is None:
            return jsonify({'error': 'Saree not found'}), 404
        saree_image = get_image_from_s3_as_link(saree.get('design_s3_key'))
        return jsonify({'data': saree_image}) , 200
    except Exception as e:
        print(e)
        return jsonify({'error': "Server error: " + str(e)}), 503




#Create saree
@app.route("/api/saree/design" , methods=['POST'])
def create_design():
    """Funtion used to create saree 
     Endpoint : /api/saree/design
     Function name : create_design
     Method : POST
     Data : border_ids , pallu_ids , body_ids , prompt , user_id
     return : 
      400 if invalid request,
      503 if server error
      200 if success
    On success returns : 
    {
saree_key' : KEY_SAREE , 
"design_id" : design Id , 
"uuid_id" :combination Id
    }
    """
    try:
        data = request.get_json()
        border_ids = data.get("border_ids")
        pallu_ids = data.get("pallu_ids")
        body_ids = data.get("body_ids")
        prompt = data.get("prompt")
        user_id = data.get("user_id")
        #Find user by id
        user =  User.find_one({"_id": ObjectId(user_id)})
        if user is None :
            #User not found
            return jsonify({'error ' : "Not Allowed"}) , 405
        combinations =[]
        #If no border_ids , body_ids , pallu_ids and prompt is empty (Note : At this case atleast prompt should be present)
        if len(border_ids) == 0 and len(body_ids) == 0 and len(pallu_ids) == 0 and (prompt is None or prompt == ""):
            #Invalid request
            return jsonify({'error': "Invalid request"}) , 400
        if len(border_ids) == 0 and len(body_ids) == 0 and len(pallu_ids) == 0:
            #No combinations
            combinations = []
        else :
            #Generating combinations
            if len(border_ids) == 0 :
                border_ids = [None]
            if len(body_ids) == 0 :
                body_ids = [None]
            if len(pallu_ids) == 0 :
                pallu_ids = [None]            
            for border_id in border_ids:
                #Checking if border is available
                if border_id is not None and not is_border_available(border_id):
                    continue
                for body_id in body_ids:
                    #Checking if body is available
                    if body_id is not None and not is_body_available(body_id):
                        continue
                    for pallu_id in pallu_ids:
                        #Checking if pallu is available
                        if pallu_id is not None and not is_pallu_available(pallu_id):
                            continue
                        #Adding combination
                        combinations.append(
                            {
                                "border_id" : border_id,
                                "body_id" : body_id,
                                "pallu_id" : pallu_id
                            }
                        )
        uuid_id = f"{uuid.uuid4().hex}"
        Combinations.insert_one({
            "uuid_id" : uuid_id ,
            "user_id" : user_id,
            "combinations" : combinations,
            "used_combination" : [],
            "saree_info" : {
                "prompt" : prompt,
                "body_ids" : body_ids,
                "border_ids" : border_ids,
                "pallu_ids" : pallu_ids
            },
            "saree_ids" : []
        })
        #Simulation of generation saree
        #Generate saree using first combinations 
        try:
            # saree_image , saree_uuid_id = generetorFull.mock_generation()
            #Getting images from the S3
            #Checking if border is available
            border_image_key =  Assests.find_one({'uuid_name':  combinations[0]['border_id'] , "asset_type" : "body"})
            #Checking if body is available
            body_image_key = Assests.find_one({'uuid_name':  combinations[0]['body_id'] , "asset_type" : "body"})
            #Checking if pallu is available
            pallu_image_key = Assests.find_one({'uuid_name':  combinations[0]['pallu_id'] , "asset_type" : "pallu"})
            
            #Getting images from the S3
            if border_image_key is None :
                border_image = None
            else:
                border_image = get_image_from_s3(border_image_key.get('original_s3_key'))
            #Checking if body is available
            if body_image_key is None :
                body_image = None
            else:
                body_image = get_image_from_s3(body_image_key.get('original_s3_key'))
            #Checking if pallu is available
            if pallu_image_key is None :
                pallu_image = None
            else:
                pallu_image = get_image_from_s3(pallu_image_key.get('original_s3_key'))
            #Generating saree
            #Mock generation
            #Comment the below line for actual generation
            saree_image , saree_uuid_id = generetorFull.mock_generation(border_image , body_image , pallu_image , prompt , aspect_ratio)
            
            
            #Uncomment the below line for actual generation
            # saree_image , saree_uuid_id = generetorFull.predict_image(saree_border=border_image , saree_body=body_image , saree_pallu=pallu_image , custom_prompt=prompt , aspect_ratio=aspect_ratio)
            if saree_image is None:
                return jsonify({'error': "Server Can't Generate Saree: "}), 503
        except Exception as e:
            return jsonify({'error': "Server Can't Generate Saree: " + str(e)}), 500
        try :
            #Saving saree in S3
            combinations = Combinations.find_one({"uuid_id" : uuid_id})
            #Change the used combination for a random combination which is not in used_combination
            used_combination = combinations.get("combinations")[0]
            #Creating key for saree for S3
            KEY_SAREE = UPLOAD_SAREE + f'{saree_uuid_id}'
            buffer = BytesIO()
            #Saving saree in S3
            upload_in_memory_image(saree_image ,KEY_SAREE )    
            #Saving saree in buffer
            saree_image.save(buffer, format="PNG")
            buffer.seek(0)
            img_str = base64.b64encode(buffer.read()).decode("utf-8")
            
        except Exception as e:
            return jsonify({'error': "Server Save Saree: " + str(e)}), 500
        
        new_design = {
                "design_id" : str(uuid.uuid4()),
                "design_s3_key" : KEY_SAREE,
                "templete_s3_key" : None,
                "border_id" : border_id ,
                "pallu_id" : pallu_id,
                "body_id":body_id,
                "created_at" : datetime.now(timezone.utc),
                "user" : user_id
            }
        #Saving saree in database
        try : 
            Designs.insert_one(new_design)
        except Exception as e:
            return jsonify({'error': "Server Save Saree: " + str(e)}), 500
        
        #Saving saree description in database
        image_bytes = buffer.getvalue()
        thread = threading.Thread(
            target=get_saree_description,
            args=(new_design["design_id"], image_bytes, user_id),
            daemon=True  # optional, so thread dies when main process exits
        )
        thread.start()
        #Updating combinations in database
        try:
            #Updating combinations in database
            Combinations.update_one({"uuid_id" : uuid_id} , {"$push" : {"used_combination" : used_combination , "saree_ids" : new_design["design_id"]}})
            combinations = Combinations.find_one({"uuid_id" : uuid_id})
        except Exception as e:
            #Deleting saree from S3
          
            Combinations.delete_one({"uuid_id" : uuid_id})
            Designs.delete_one({"design_id" : new_design["design_id"]})
            return jsonify({'error': "Server Save Saree: " + str(e)}), 500
        return jsonify({'saree_key' : KEY_SAREE , "design_id" : new_design["design_id"] , "uuid_id" : uuid_id}) , 200
        
    except Exception as e:
        return jsonify({'error': "Server error: " + str(e)}), 503

#Regenerate Saree
@app.route("/api/saree/design/<uuid_id>" , methods=["POST"])
def regenerate_design(uuid_id):
    """Regenerate Saree
      Funtion used to regenerate saree 
     Endpoint : /api/saree/design/<uuid_id>
     Function name : regenerate_design
     Method : POST
     Data : uuid_id , prompt , user_id
     return : 
      400 if invalid request,
      503 if server error
      200 if success
    On success returns : 
    {
    "saree_key" : KEY_SAREE , 
    "design_id" : design Id , 
    "uuid_id" :combination Id
    }
   
    
    """
    data = request.get_json()
    user_id = data.get("user_id")

    current_prompt = data.get("prompt")
    
    print(user_id , current_prompt)
    #Find the user by id and check if the user is valid
    user =  User.find_one({"_id": ObjectId(user_id)})
    if user is None:
        return jsonify({'error': "User not found"}), 404
    try:
        #Find the combinations by uuid_id and check if the combinations is valid
        combinations_data = Combinations.find_one({"uuid_id" : uuid_id})
        if combinations_data is None:
            return jsonify({'error': "Saree not found"}), 404
        
        #Get the combinations and used_combination
        combinations = combinations_data.get("combinations")
        used_combination = combinations_data.get("used_combination")
        #Get the index of the used_combination 
        index = len(used_combination) % len(combinations)
        print(index)
        #Get the combination at the index
        combination = combinations[index]
        #Get the border_id , body_id , pallu_id from the combination
        border_id = combination.get("border_id")
        body_id = combination.get("body_id")
        pallu_id = combination.get("pallu_id")
        #Get the prompt from the combinations_data
        prompt = combinations_data.get("saree_info").get("prompt")
        #Get the previous design id from the combinations_data
        previous_design_id = combinations_data.get("saree_ids")[-1]
        previous_design_data = Designs.find_one({"design_id" : previous_design_id})
        previous_saree = get_image_from_s3(previous_design_data.get("design_s3_key"))
        try:
            #Getting images from the S3
            #Get the border image from the S3
            border_image_key =  Assests.find_one({'uuid_name': border_id, "asset_type" : "border"})
            #Get the body image from the S3
            body_image_key = Assests.find_one({'uuid_name': body_id , "asset_type" : "body"})
            #Get the pallu image from the S3
            pallu_image_key = Assests.find_one({'uuid_name': pallu_id , "asset_type" : "pallu"})
            #Get the border image from the S3
            if border_image_key is None :
                border_image = None
            else:
                border_image = get_image_from_s3(border_image_key.get('original_s3_key'))
            #Get the body image from the S3
            if body_image_key is None :
                body_image = None
            else:
                body_image = get_image_from_s3(body_image_key.get('original_s3_key'))
            if pallu_image_key is None :
                pallu_image = None
            else:
                pallu_image = get_image_from_s3(pallu_image_key.get('original_s3_key'))
            #Regenerate the saree
            #Mock generation
            #Comment the below line for actual generation
            saree_image , saree_uuid_id = generetorFull.mock_generation(border_image , body_image , pallu_image , prompt , aspect_ratio , previous_saree)


            #Uncomment the below line for actual generation
            #saree_image , saree_uuid_id = generetorFull.regenerate_image(saree_border=border_image , saree_body=body_image , saree_pallu=pallu_image , currect_prompt=current_prompt,prompt=prompt , previous_saree=previous_saree,aspect_ratio=aspect_ratio)
            KEY_SAREE = UPLOAD_SAREE + f'{saree_uuid_id}'
            if saree_image is None:
                return jsonify({'error': "Server Can't Generate Saree: "}), 503
            try :
                #Svaing new design and updateing the combinations
                buffer = BytesIO()
                saree_image.save(buffer, format="PNG")
                buffer.seek(0)
                upload_in_memory_image(saree_image , KEY_SAREE)
                new_design = {
                    "design_id" : str(uuid.uuid4()),
                    "design_s3_key" : KEY_SAREE,
                    "templete_s3_key" : None,
                    "border_id" : border_id ,
                    "pallu_id" : pallu_id,
                    "body_id":body_id,
                    "created_at" : datetime.now(timezone.utc),
                    "user" : user_id
                }
                try : 
                    Designs.insert_one(new_design)
                except Exception as e:
                    return jsonify({'error': "Server Save Saree: " + str(e)}), 500
                
                image_bytes = buffer.getvalue()
                thread = threading.Thread(
                    target=get_saree_description,
                    args=(new_design["design_id"], image_bytes, user_id),
                    daemon=True  # optional, so thread dies when main process exits
                )
                thread.start()
                try:
                    Combinations.update_one({"uuid_id" : uuid_id} , {"$push" : {"used_combination" : used_combination , "saree_ids" : new_design["design_id"]}})
                    combinations = Combinations.find_one({"uuid_id" : uuid_id})
                except Exception as e:
                    Combinations.delete_one({"uuid_id" : uuid_id})
                    Designs.delete_one({"design_id" : new_design["design_id"]})

                    return jsonify({'error': "Server Save Saree: " + str(e)}), 500
                return jsonify({'saree_key' : KEY_SAREE , "design_id" : new_design["design_id"] , "uuid_id" : uuid_id}) , 200
            except Exception as e:
                return jsonify({'error': "Server Can't Save Saree: " + str(e)}), 500
        except Exception as e:
            return jsonify({'error': "Server Can't Generate Saree: " + str(e)}), 500
    except Exception as e:
        return jsonify({'error': "Server error: " + str(e)}), 503






        
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    # ADD THIS PRINT LINE TO DEBUG
    print(f"User asked for: {path}") 
    print(f"Looking in folder: {app.static_folder}")
    
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    
    # ADD THIS PRINT LINE
    print("File not found, serving index.html")
    return send_from_directory(app.static_folder, 'index.html')




if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 