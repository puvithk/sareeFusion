from flask_mongoengine import MongoEngine
from datetime import datetime
import uuid

# Initialize the object, but don't connect here. 
# The connection happens in app.py
db = MongoEngine()

class User(db.Document):
    # Provides a link between the raw files and a specific person
    public_id = db.StringField(default=lambda: str(uuid.uuid4()), unique=True)
    email = db.StringField(required=True, unique=True)
    password_hash = db.StringField(required=True)
    created_at = db.DateTimeField(default=datetime.utcnow)
    
    meta = {'collection': 'users'}

class Asset(db.Document):
    # Stores info about Uploaded Borders, Pallus, and Bodies
    uuid_name = db.StringField(required=True, unique=True) # The filename ID
    user = db.ReferenceField(User, required=True) # Link to User
    
    asset_type = db.StringField(required=True, choices=('border', 'pallu', 'body'))
    
    # S3 File Paths
    original_s3_key = db.StringField(required=True)
    vector_s3_key = db.StringField()
    
    created_at = db.DateTimeField(default=datetime.utcnow)
    
    meta = {'collection': 'assets'}

class Design(db.Document):
    # Stores the final Generated Saree info
    saree_id = db.StringField(required=True, unique=True)
    user = db.ReferenceField(User, required=True) # Link to User
    
    # Link back to the specific ingredients used
    border_used = db.ReferenceField(Asset)
    pallu_used = db.ReferenceField(Asset)
    body_used = db.ReferenceField(Asset)
    
    prompt = db.StringField()
    
    # S3 File Paths
    template_s3_key = db.StringField()
    final_saree_s3_key = db.StringField(required=True)
    
    created_at = db.DateTimeField(default=datetime.utcnow)
    
    meta = {'collection': 'designs'}