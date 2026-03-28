# =============================================================================
# Gallraio - THE IMAGE SHARING APPLICATION - FLASK WEB APP                    =
# =============================================================================
# This is a social media-style image sharing application built with Flask.
# Features: User registration/login, image uploads, likes/dislikes, comments,
# notifications, and user profiles with editable descriptions.

# Made by Nezar Bahid -- CEO of Coco-devs @ AUI 
# =============================================================================
from src.backend.routing.webpages import web
from src.backend.routing.api import api
from src.backend.Config import app
# =============================================================================
# APPLICATION STARTUP                                                         =
# =============================================================================

app.register_blueprint(web)
app.register_blueprint(api)
