import os                     # File system operations
# Flask framework imports
from flask import Flask


# =============================================================================
# APPLICATION CONFIGURATION
# =============================================================================
# Initialize Flask application

app = Flask(__name__,template_folder="../templates",static_folder="../static")
# Secret key for session management and security
app.secret_key = "F18029BD1E955FB23095506A7223710A90B5F43E1F57442EB3ECC8D704B8554D"

# Point to the project root, not the script folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Define folder paths for file storage
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")  # User uploaded images
AVATAR_FOLDER = os.path.join(BASE_DIR, "static", "avatars")  # User profile pictures
# Allowed file extensions for security
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

# Create necessary directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(AVATAR_FOLDER, exist_ok=True)

# Database file path
DB_PATH = os.path.join(BASE_DIR, "database.db")