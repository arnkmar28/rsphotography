import os
from dotenv import load_dotenv

load_dotenv()

# Secret key for sessions
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-very-secret')

# Admin Password
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

# Database Config (Neon/Postgres)
DATABASE_URL = os.environ.get('DATABASE_URL')

# Cloudinary Config
CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME')
CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY')
CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET')
