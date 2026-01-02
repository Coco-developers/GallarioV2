import math, sqlite3
from ..Helpers import (
    get_db, current_user, save_avatar_file, send_from_directory
)
from werkzeug.security import generate_password_hash, check_password_hash
from ..Config import (UPLOAD_FOLDER)
from flask import (
    session, Blueprint, request, render_template, url_for, redirect,
    flash, jsonify
)

web = Blueprint("main", __name__, url_prefix="/")

@web.route("/")
def index():
    """
    Main page - displays the feed of all posts with pagination.
    Shows posts with like/dislike counts, comment counts, and user vote status.
    """
    db = get_db()
    user_id = session.get("user_id")
    #Sort by arg
    sortby = request.args.get("sortby", "time")
    accending = int(request.args.get("accending", 1))
    # Get number of posts
    total_posts = db.execute("SELECT COUNT(*) FROM posts").fetchone()[0] 
    # Pagination setup
    page = int(request.args.get("page", 1))
    per_page = 5  # Posts per page
    offset = (page - 1) * per_page

    # Complex query to get posts with all related data
    posts = db.execute("""
        SELECT posts.id, posts.image, posts.caption, posts.timestamp, posts.user_id,
                users.username, users.avatar,
                -- Count likes (value = 1)
                COALESCE((SELECT COUNT(*) FROM likes WHERE likes.post_id = posts.id AND likes.value = 1),0) AS like_count,
                -- Count dislikes (value = -1)
                COALESCE((SELECT COUNT(*) FROM likes WHERE likes.post_id = posts.id AND likes.value = -1),0) AS dislike_count,
                -- Get current user's vote on this post
                COALESCE((SELECT value FROM likes WHERE likes.post_id = posts.id AND likes.user_id = ?), 0) AS user_vote,
                -- Count comments on this post
                COALESCE((SELECT COUNT(*) FROM comments WHERE comments.post_id = posts.id),0) AS comment_count
        FROM posts
        JOIN users ON posts.user_id = users.id
        ORDER BY posts.timestamp DESC
        LIMIT ? OFFSET ?
    """, (user_id, per_page, offset)).fetchall()

    db.close()
    return render_template("index.html", posts=posts, user=current_user(), page=page, total_posts=total_posts, total_pages=math.ceil(total_posts / per_page))

@web.route("/post/<int:post_id>")
def view_post(post_id):
    """
    Display a single post with its comments and reaction counts.
    Shows the full post details, all comments, and user's current reaction.
    """
    db = get_db()
    
    # Get the post with author information
    post = db.execute("""
        SELECT posts.*, users.username, users.avatar
        FROM posts JOIN users ON posts.user_id = users.id
        WHERE posts.id = ?
    """, (post_id,)).fetchone()
    
    if not post:
        db.close()
        return "Post not found", 404

    # Get all comments for this post with author info
    comments = db.execute("""
        SELECT comments.*, users.username, users.avatar
        FROM comments JOIN users ON comments.user_id = users.id
        WHERE comments.post_id = ?
        ORDER BY comments.timestamp ASC
    """, (post_id,)).fetchall()

    # Get reaction counts
    like_count = db.execute("SELECT COUNT(*) AS c FROM likes WHERE post_id = ? AND value = 1", (post_id,)).fetchone()["c"]
    dislike_count = db.execute("SELECT COUNT(*) AS c FROM likes WHERE post_id = ? AND value = -1", (post_id,)).fetchone()["c"]

    # Get current user's reaction to this post
    user_vote_row = None
    user_vote = 0
    uid = session.get("user_id")
    if uid:
        user_vote_row = db.execute("SELECT value FROM likes WHERE post_id = ? AND user_id = ?", (post_id, uid)).fetchone()
        if user_vote_row:
            user_vote = user_vote_row["value"] or 0

    db.close()
    return render_template("independent/post.html", post=post, comments=comments, like_count=like_count, dislike_count=dislike_count, user_vote=user_vote, user=current_user())

@web.route("/logout")
def logout():
    """
    Log out the current user by clearing the session.
    Redirects to login page.
    """
    session.clear()  # Remove all session data
    return redirect(url_for("main.login"))

@web.route("/profile/<username>")
def profile(username=None):
    """
    Display a user's profile page with their posts.
    Shows user info, avatar, description, and all their posts.
    If no username provided, redirects to current user's profile.
    """
    # Handle case where no username is provided
    if username is None:
        user = current_user()
        if not user:
            return redirect(url_for("main.login"))
        return redirect(url_for("main.profile", username=user["username"]))

    db = get_db()
    
    # Get the profile user's information
    profile_user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    if not profile_user:
        db.close()
        return "Error user not found.", 404
    
    # Get all posts by this user
    posts = db.execute("SELECT * FROM posts WHERE user_id = ? ORDER BY timestamp DESC", (profile_user["id"],)).fetchall()
    db.close()
    
    return render_template("independent/profile.html", profile=profile_user, posts=posts, user=current_user())


@web.route("/uploads/<filename>")
def uploaded_file(filename):
    """
    Serve uploaded image files to the browser.
    This route allows the frontend to display uploaded images.
    """
    return send_from_directory(UPLOAD_FOLDER, filename)

@web.route("/notifications", methods=["GET"])
def get_notifications():
    """
    Get all notifications for the current user.
    Returns JSON with notification data including post/comment details.
    Used by the notification sidebar to display recent activity.
    """
    # Check authentication
    user = current_user()
    if not user:
        return jsonify(success=False, error="Unauthorized"), 401

    db = get_db()
    
    # Complex query to get notifications with all related data
    notifications = db.execute("""
        SELECT n.id,
               n.type,                    -- 0=like, 1=dislike, 2=comment, 3=dm
               n.reference_id,           -- Post ID being referenced
               n.seen,                   -- Whether notification was read
               n.created_at,             -- When notification was created
               n.comment_id AS notif_comment_id,  -- Comment ID for comment notifications
               u.username AS maker_username,     -- Who triggered the notification
               u.avatar   AS maker_avatar,       -- Avatar of the notification maker
               p.id AS post_id,                 -- Post being referenced
               p.image AS post_image,            -- Post image
               c.id AS comment_row_id,          -- Comment details
               c.text AS comment_content         -- Comment text
        FROM notifications n
        JOIN users u ON n.maker_id = u.id        -- Get notification maker info
        LEFT JOIN posts p ON n.reference_id = p.id  -- Get post info
        LEFT JOIN comments c ON n.comment_id = c.id  -- Get comment info
        WHERE n.receiver_id = ?                   -- Only notifications for current user
        ORDER BY n.created_at DESC                -- Most recent first
    """, (user["id"],)).fetchall()
    db.close()

    # Format notifications for JSON response
    data = []
    for n in notifications:
        item = {
            "id": n["id"],
            "type": n["type"],
            "reference_id": n["reference_id"],
            "seen": bool(n["seen"]),
            "created_at": n["created_at"],
            "maker": {
                "username": n["maker_username"],
                "avatar": n["maker_avatar"]
            },
            "post": {
                "id": n["post_id"],
                "image": n["post_image"]
            }
        }

        # Add comment details for comment notifications
        if n["type"] == 2:  # comment notification
            item["comment"] = {
                "id": n["notif_comment_id"],
                "content": n["comment_content"]
            }

        data.append(item)

    return jsonify(success=True, notifications=data)

@web.route("/legal")
def legal():
    return render_template("ect/legal_agreement.html")

@web.route("/download")
def download_webthingy():
    return render_template("ect/download.html")

@web.route("/login", methods=["GET", "POST"])
def login():
    """
    User login page and authentication.
    GET: Show login form
    POST: Process login credentials and authenticate user
    """
    if request.method == "POST":
        # Get form data
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        
        # Check user credentials
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        db.close()
        
        # Verify password hash
        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]  # Start user session
            return redirect(url_for("main.index"))
        else:
            flash("Invalid username or password", "error")
    
    # Show login form (GET request or failed POST)
    return render_template("actions/login.html", register=False, user=current_user())

@web.route("/register", methods=["GET", "POST"])
def register():
    """
    User registration page and account creation.
    GET: Show registration form
    POST: Create new user account with optional avatar
    """
    if request.method == "POST":
        # Get form data
        username = request.form.get("username", "").strip()
        password_raw = request.form.get("password", "")
        avatar_file = request.files.get("avatar")  # Optional avatar upload

        # Validate required fields
        if username == "" or password_raw == "":
            flash("Username and password required.", "error")
            return redirect(url_for("main.register"))

        # requires 8 characters or more
        if len(password_raw) < 8 :
            flash("password must be atleast 8 characters.", "error")
            return redirect(url_for("main.register")) 
        elif len(username) < 3:
            flash("Username must be atleast 3 characters.", "error")
            return redirect(url_for("main.register")) 
        
        # Process avatar if provided
        avatar_path = save_avatar_file(avatar_file) if avatar_file else "images/default_pfp.png"
        
        # Create user account
        db = get_db()
        try:
            db.execute(
                "INSERT INTO users (username, password, avatar, description) VALUES (?, ?, ?, ?)",
                (username, generate_password_hash(password_raw), avatar_path, None)
            )
            db.commit()
            flash("Account created. Please log in.", "success")
            db.close()
            return redirect(url_for("main.login"))
        except sqlite3.IntegrityError:
            # Username already exists
            db.close()
            flash("Username already taken.", "error")
            return redirect(url_for("main.register"))

    # Show registration form (GET request or failed POST)
    return render_template("actions/login.html", register=True, user=current_user())

@web.route("/delete_account")
def delete_account():
    return render_template("actions/DelAcc.html")