# Gallario - Social Media Image Sharing Platform - Made by Nezar

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A modern, feature-rich social media platform built with Flask that allows users to share images, interact with posts, and connect with others through a clean, responsive interface.

## Features

### User Management
- **Secure Registration & Login** - Password hashing with Werkzeug
- **Profile Customization** - Upload avatars and edit descriptions
- **Session Management** - Secure user authentication

### Core Functionality
- **Image Upload** - Support for PNG, JPG, JPEG, GIF formats
- **Post Feed** - Paginated timeline with latest posts first
- **Interactive Posts** - Like/dislike system with real-time updates
- **Comments System** - Engage with posts through threaded comments

### Notifications
- **Real-time Notifications** - Get notified for likes, dislikes, and comments
- **Interactive Sidebar** - Slide-out notification panel
- **Mark as Read** - Click to mark notifications as seen

### User Experience
- **Responsive Design** - Works on desktop and mobile devices
- **Dark Theme** - Modern, eye-friendly interface
- **Image Processing** - Automatic avatar cropping and resizing
- **File Management** - Secure file uploads with validation

## Quick Start

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/Gallario.git
   cd Gallario
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:8080`

## Or if you have Linux(very cool)
just run this in whatever folder you want :
```
sudo apt update
sudo apt install python3
sudo apt install python3-flask
sudo apt install python3-pillow
sudo apt install python3-werkzeug
sudo apt install git
git clone https://github.com/yourusername/Gallario.git
cd Gallario
python3 app.py
```
Then you can see the ip adress on the terminal, type the same thing into any other device that is also connected to the same network.
## Requirement
Have Python and download all the libraries from `requirements.txt` file.

##  Project Structure

```
Gallario/
.
├── app.py                       # What to run
├── LICENSE                      # Code license
├── README.md                    # This file, info about the repo
├── requirements.txt             # What Libraries that need to be installed to run the project
└── src                          # src -> short for source -> short for source code
    ├── backend                  # Backend where it is in python, Server logic
    │   ├── Config.py            # Web app configiruation file
    │   ├── Helpers.py           # Function that make code smaller
    │   └── Routing.py           # Main logic file, here the serveing happens
    ├── database.db              # This is auto-created it does not exist now. The SQLite Database
    ├── static                   # Anything put in here is accesible by the anyone in the website.
    │   ├── avatars/             # Auto-created folder where user avatars are stored
    │   ├── favico.ico           # Website icon
    │   ├── fonts/               # Folder for fonts
    │   │   ├── Biome.ttf        # My favorite font
    │   │   └── google_font.ttf  # Font made by google
    │   ├── images/              # Website images
    │   │   ├── background.jpg   # The website background
    │   │   ├── default_pfp.png  # The user's default profile picture
    │   │   ├── icondevs.jpg     # The company's logo
    │   │   └── logo.png         # The old website logo
    │   ├── javascript/          # Javascript folder, used in HTML
    │   │   ├── change_desc.js   # To be used on `profile.html` where it allows profile description change
    │   │   ├── code.js          # Generic script file, houses various functions
    │   │   ├── markdown.js      # An AI written script, used to turn `.md` file into `html` on the client's side
    │   │   ├── post_index.js    # Another generic script, to be used on `index.html`
    │   │   └── tailwindcss.js   # A library used for styling, not written for readability
    │   ├── legal/               # Folder to house legal files
    │   │   └── legal.md         # Main agreement, used on `/register`
    │   ├── styling/             # Styling folder, houses CSS files
    │   │   ├── google.css       # Google css file
    │   │   ├── index.css        # Old-school css
    │   │   └── new.css          # Newer css
    │   └── uploads/             # Auto-created folder, houses uploades and their thumbnails
    └── templates                # Folder for HTML
        ├── actions/login.html       # Used for either loggin in, and registering
        ├── ect/download.html        # Used for the android app download
        ├── ect/legal_agreement.html # User to show the legal aggrement
        ├── fragments/layout.html    # This template was made to be the navigation bar, but just one file uses it
        ├── fragments/side.html      # Another Template, used for notifications
        ├── independent/post.html    # Used to look at a post
        ├── independent/profile.html # Used to look at users's profile
        └── index.html               # Used for showing off the Main Feed
```

## Database Schema

The application uses SQLite with the following tables:

- **users** - User accounts and profiles
- **posts** - Image posts with captions
- **likes** - User reactions (like/dislike system)
- **comments** - Post comments
- **notifications** - User notifications
- **dms** - Direct messages (future feature)

## Configuration

### Ternimal Running
You can change what way you run the Web app.

```bash
usage: app.py [--server] [--port PORT] 
options:
  --port PORT  Port number to run on the web app.
  --server     Set it to True if you're hosting this on a server.
```


### Security - consider doing
- Change the `app.secret_key` in production
- Use environment variables for sensitive data
- Consider using HTTPS in production

## Why Gallario ?

### For Users
1. **Register** - Create a new account with username and password
2. **Login** - Access your account
3. **Upload** - Share images with captions
4. **Interact** - Like, dislike, and comment on posts
5. **Customize** - Update your profile and avatar
6. **Stay Updated** - Check notifications for activity

### For Developers
1. **Modular Design** - Easy to extend with new features
2. **Clean Code** - Well-commented and documented
3. **Database Migrations** - Automatic schema updates
4. **Error Handling** - Graceful error management

## Development
Don't.

### Common Issues

**Port already in use**
Kill the Python... I mean the python process.

**Database errors**
```bash
# Delete database.db to reset
run this
rm database.db
```

**File upload issues**
- Check file permissions on the folder that the project in on
- Ensure allowed file extensions match your desired uploads

## Contributing

1. Don't

## License

This project may be licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author(me)

**Nezar Bahid**
- Email: n.bahid@aui.ma
- Institution: Coco-devs

## Acknowledgments

- Flask community for the excellent framework
- Contributors and testers(Chatgpt and Cursor and maybe Gemini)
- Open source libraries used in this project


## What's next ?
Check the issues on the github webpage

---

⭐ **Star this repository if you found it helpful!**

📧 **Contact me for questions or collaboration opportunities.**


© 2025-2026 Coco-devs. All rights reserved.
