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
from src.backend.Config import app, arg
import os
# =============================================================================
# APPLICATION STARTUP                                                         =
# =============================================================================

app.register_blueprint(web)
app.register_blueprint(api)
if __name__ == "__main__":
    """
    Start the Flask development server.
    - host="0.0.0.0" allows external connections (for testing on network) also can be turned off in terminal
    - port=8080 is the server port unless changed on the Terminal
    - debug=True enables auto-reload and detailed error pages
    """
    if arg.server or os.path.exists("server"):
        # For network access (development/testing):
        print("Running as a server")
        app.run(port=arg.port, debug=False, host="0.0.0.0")
    elif arg.debug:
        # For debugging on local server, used for testing on smartphones
        app.run(port=arg.port, debug=True, host="0.0.0.0")
    else:
        # For local development only:
        app.run(port=arg.port, debug=True)
