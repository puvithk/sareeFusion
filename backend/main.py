from asyncio import threads
import io
import json
import threading
from flask import Flask, request, jsonify, send_file
from datetime import datetime, timezone

from flask_pymongo import PyMongo
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
import boto3
from bson.objectid import ObjectId #
load_dotenv()
app = Flask(__name__)
frontend_url ="https://sareefusion-frontend.onrender.com"
CORS(app, origins=[frontend_url , "*"])
S3_BUCKET_NAME = 'sareefusion'
app.config['MONGO_URI'] =  os.environ.get('MONGO_URI')

mongo = PyMongo(app)
db = mongo.db

User = db.users
Assests = db.assests
Designs = db.designs
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
# --- 1. Health Check Endpoint ---
# Purpose: Verify Flask is running.
aspect_ratio = get_image_from_s3("reference image/reference_image.png")

def get_saree_description(design_id, image_bytes, user):

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
        print(sarees)
        for saree in sarees:
            print(saree)
            print()
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 