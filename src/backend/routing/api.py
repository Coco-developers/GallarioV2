import sqlite3, time
from ..Helpers import (
    get_db, current_user, allowed_file, save_upload_file,
    remove_upload_file
)
from flask import (
    session, Blueprint, request, url_for, redirect,
    flash, jsonify, current_app
)
from werkzeug.security import check_password_hash


api = Blueprint("api", __name__, url_prefix="/")
@api.route("/upload", methods=["POST"])
def upload():
    """
    Handle image uploads for new posts.
    Requires user to be logged in.
    Validates file type and saves to database.
    """
    # Check if user is logged in
    user = current_user()
    if not user:
        return redirect(url_for("main.login"))

    # Get uploaded file
    file = request.files.get("photo")
    if not file:
        flash("No file uploaded.", "error")
        return redirect(url_for("main.index"))

    # Validate file type
    if not allowed_file(file.filename):
        flash("Invalid file type.", "error")
        return redirect(url_for("main.index"))

    # Save the file
    stored_filename = save_upload_file(file)
    if not stored_filename:
        flash("Failed to save file.", "error")
        return redirect(url_for("main.index"))

    # Get caption and save post to database
    caption = request.form.get("caption", "").strip()
    db = get_db()
    db.execute(
        "INSERT INTO posts (user_id, image, caption) VALUES (?, ?, ?)",
        (user["id"], stored_filename, caption)
    )
    db.commit()
    db.close()
    flash("Uploaded!", "success")
    return redirect(url_for("main.index"))

@api.route("/profile/avatar", methods=["POST"])
def change_avatar():
    """
    Handle avatar upload/change for the current user.
    Processes the image, resizes it, and updates the user's avatar in the database.
    """
    # Check authentication
    user = current_user()
    if not user:
        return redirect(url_for("main.login"))
    
    # Get uploaded avatar file
    avatar_file = request.files.get("avatar")
    if not avatar_file or avatar_file.filename == "":
        flash("No file selected.", "error")
        return redirect(url_for("main.profile", username=user["username"]))
    
    # Process and save the avatar
    avatar_path = save_avatar_file(avatar_file)
    if not avatar_path:
        flash("Invalid avatar file.", "error")
        return redirect(url_for("main.profile", username=user["username"]))
    
    # Update user's avatar in database
    db = get_db()
    db.execute("UPDATE users SET avatar = ? WHERE id = ?", (avatar_path, user["id"]))
    db.commit()
    db.close()
    
    flash("Avatar updated!", "success")
    return redirect(url_for("main.profile", username=user["username"]))

@api.route("/like/<int:post_id>", methods=["POST"])
def like(post_id):
    user = current_user()
    if not user:
        return jsonify(success=False), 401

    db = get_db()
    # let SQLite wait a bit for locks instead of failing immediately
    try:
        db.execute("PRAGMA busy_timeout = 5000")  # milliseconds
        db.execute("PRAGMA journal_mode = WAL")
    except Exception:
        # pragma may fail on some configurations; ignore if it does
        pass

    post = db.execute("SELECT user_id FROM posts WHERE id = ?", (post_id,)).fetchone()
    if not post:
        return jsonify(success=False, error="Post not found"), 404

    # retry loop for transient locking issues
    retries = 6
    backoff_base = 0.02
    for attempt in range(retries):
        try:
            existing = db.execute(
                "SELECT id, value FROM likes WHERE user_id = ? AND post_id = ?",
                (user["id"], post_id)
            ).fetchone()

            if existing:
                if existing["value"] == 1:
                    # toggle off
                    db.execute("DELETE FROM likes WHERE id = ?", (existing["id"],))
                else:
                    # change dislike -> like
                    db.execute("UPDATE likes SET value = 1 WHERE id = ?", (existing["id"],))
                    if post["user_id"] != user["id"]:
                        db.execute(
                            "INSERT INTO notifications (maker_id, receiver_id, type, reference_id) VALUES (?, ?, ?, ?)",
                            (user["id"], post["user_id"], 0, post_id)
                        )
            else:
                # try to insert; use upsert fallback in case of race below
                db.execute("INSERT INTO likes (user_id, post_id, value) VALUES (?, ?, 1)",
                           (user["id"], post_id))
                if post["user_id"] != user["id"]:
                    db.execute(
                        "INSERT INTO notifications (maker_id, receiver_id, type, reference_id) VALUES (?, ?, ?, ?)",
                        (user["id"], post["user_id"], 0, post_id)
                    )

            db.commit()
            break  # success -> exit retry loop

        except sqlite3.IntegrityError:
            # Rare race: someone else inserted the same (user_id,post_id) at the same time.
            # Use upsert to set the correct value (1).
            db.execute("""
                INSERT INTO likes (user_id, post_id, value)
                VALUES (?, ?, 1)
                ON CONFLICT(user_id, post_id) DO UPDATE SET value=excluded.value
            """, (user["id"], post_id))
            if post["user_id"] != user["id"]:
                db.execute(
                    "INSERT INTO notifications (maker_id, receiver_id, type, reference_id) VALUES (?, ?, ?, ?)",
                    (user["id"], post["user_id"], 0, post_id)
                )
            db.commit()
            break

        except sqlite3.OperationalError as e:
            # transient lock - backoff and retry
            if attempt == retries - 1:
                current_app.logger.exception("DB locked when processing like")
                return jsonify(success=False, error="database is locked"), 500
            time.sleep(backoff_base * (2 ** attempt))
            continue

    # updated counts
    like_count = db.execute("SELECT COUNT(*) FROM likes WHERE post_id = ? AND value = 1", (post_id,)).fetchone()[0]
    dislike_count = db.execute("SELECT COUNT(*) FROM likes WHERE post_id = ? AND value = -1", (post_id,)).fetchone()[0]

    try:
        db.close()
    except Exception:
        pass

    return jsonify(success=True, like_count=like_count, dislike_count=dislike_count)

@api.route("/comment/<int:post_id>", methods=["POST"])
def add_comment(post_id):
    """
    Add a new comment to a post.
    Requires user to be logged in.
    Sends notification to post owner if not self-comment.
    """
    # Check authentication
    user = current_user()
    if not user:
        flash("Login to comment.", "error")
        return redirect(url_for("main.login"))

    # Get and validate comment text
    text = request.form.get("comment", "").strip()
    if text == "":
        flash("Comment cannot be empty.", "error")
        return redirect(url_for("main.view_post", post_id=post_id))
        
    # Save comment to database
    db = get_db()
    cur = db.execute(
        "INSERT INTO comments (post_id, user_id, text) VALUES (?, ?, ?)",
        (post_id, user["id"], text)
    )
    comment_id = cur.lastrowid  # Get the ID of the new comment
    
    # Send notification to post owner (if not self-comment)
    post = db.execute("SELECT user_id FROM posts WHERE id = ?", (post_id,)).fetchone()
    if post and post["user_id"] != user["id"]:
        db.execute("""
            INSERT INTO notifications (maker_id, receiver_id, type, reference_id, comment_id)
            VALUES (?, ?, ?, ?, ?)
        """, (user["id"], post["user_id"], 2, post_id, comment_id))  # type 2 = comment
    
    db.commit()
    db.close()
    flash("Comment added!", "success")
    return redirect(url_for("main.view_post", post_id=post_id))

@api.route("/dislike/<int:post_id>", methods=["POST"])
def dislike(post_id):
    user = current_user()
    if not user:
        return jsonify(success=False), 401

    db = get_db()
    try:
        db.execute("PRAGMA busy_timeout = 5000")
        db.execute("PRAGMA journal_mode = WAL")
    except Exception:
        pass

    post = db.execute("SELECT user_id FROM posts WHERE id = ?", (post_id,)).fetchone()
    if not post:
        return jsonify(success=False, error="Post not found"), 404

    retries = 6
    backoff_base = 0.02
    for attempt in range(retries):
        try:
            existing = db.execute(
                "SELECT id, value FROM likes WHERE user_id = ? AND post_id = ?",
                (user["id"], post_id)
            ).fetchone()

            if existing:
                if existing["value"] == -1:
                    # toggle off
                    db.execute("DELETE FROM likes WHERE id = ?", (existing["id"],))
                else:
                    # change like -> dislike
                    db.execute("UPDATE likes SET value = -1 WHERE id = ?", (existing["id"],))
                    if post["user_id"] != user["id"]:
                        db.execute(
                            "INSERT INTO notifications (maker_id, receiver_id, type, reference_id) VALUES (?, ?, ?, ?)",
                            (user["id"], post["user_id"], 1, post_id)
                        )
            else:
                db.execute("INSERT INTO likes (user_id, post_id, value) VALUES (?, ?, -1)",
                           (user["id"], post_id))
                if post["user_id"] != user["id"]:
                    db.execute(
                        "INSERT INTO notifications (maker_id, receiver_id, type, reference_id) VALUES (?, ?, ?, ?)",
                        (user["id"], post["user_id"], 1, post_id)
                    )

            db.commit()
            break

        except sqlite3.IntegrityError:
            db.execute("""
                INSERT INTO likes (user_id, post_id, value)
                VALUES (?, ?, -1)
                ON CONFLICT(user_id, post_id) DO UPDATE SET value=excluded.value
            """, (user["id"], post_id))
            if post["user_id"] != user["id"]:
                db.execute(
                    "INSERT INTO notifications (maker_id, receiver_id, type, reference_id) VALUES (?, ?, ?, ?)",
                    (user["id"], post["user_id"], 1, post_id)
                )
            db.commit()
            break

        except sqlite3.OperationalError:
            if attempt == retries - 1:
                current_app.logger.exception("DB locked when processing dislike")
                return jsonify(success=False, error="database is locked"), 500
            time.sleep(backoff_base * (2 ** attempt))
            continue

    like_count = db.execute("SELECT COUNT(*) FROM likes WHERE post_id = ? AND value = 1", (post_id,)).fetchone()[0]
    dislike_count = db.execute("SELECT COUNT(*) FROM likes WHERE post_id = ? AND value = -1", (post_id,)).fetchone()[0]

    try:
        db.close()
    except Exception:
        pass

    return jsonify(success=True, like_count=like_count, dislike_count=dislike_count)

@api.route("/delete/<int:post_id>", methods=["POST"])
def delete_post(post_id):
    """
    Delete a post (owner only).
    Removes the post, all its comments, likes, and the associated image file.
    Only the post owner can delete their posts.
    """
    # Check authentication
    user = current_user()
    if not user:
        flash("Login to delete posts.", "error")
        return redirect(url_for("main.login"))

    db = get_db()
    post = db.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
    
    # Validate post exists
    if not post:
        db.close()
        flash("Post not found.", "error")
        return redirect(url_for("main.index"))
    
    # Check ownership
    if post["user_id"] != user["id"]:
        db.close()
        flash("You can only delete your own posts.", "error")
        return redirect(url_for("main.index"))

    # Delete the associated image file
    try:
        remove_upload_file(post["image"])
    except Exception:
        # Silently handle file deletion errors
        pass

    # Delete all related data (cascade delete)
    db.execute("DELETE FROM likes WHERE post_id = ?", (post_id,))      # Remove all likes
    db.execute("DELETE FROM comments WHERE post_id = ?", (post_id,))   # Remove all comments
    db.execute("DELETE FROM posts WHERE id = ?", (post_id,))          # Remove the post
    db.commit()
    db.close()

    flash("Post deleted.", "success")
    return redirect(url_for("main.index"))

@api.route("/description", methods=["POST"])
def change_description():
    """
    Update user's profile description via AJAX.
    Validates length and updates the database.
    Returns JSON response for frontend updates.
    """
    # Check authentication
    user = current_user()
    if not user:
        return jsonify(success=False, error="Unauthorized"), 401

    # Get description from JSON request
    data = request.get_json() or {}
    description = (data.get("description") or "").strip()

    # Validate description length
    if len(description) > 1000:
        return jsonify(success=False, error="Description too long (max 1000 chars)."), 400

    # Update description in database
    db = get_db()
    db.execute("UPDATE users SET description = ? WHERE id = ?", (description, user["id"]))
    db.commit()
    db.close()
    
    return jsonify({"success": True, "description": description})

@api.route("/notifications/<int:notif_id>/seen", methods=["POST"])
def mark_notification_seen(notif_id):
    """
    Mark a specific notification as seen/read.
    Used when user clicks on a notification to mark it as read.
    Returns JSON response for frontend updates.
    """
    # Check authentication")
    user = current_user()
    if not user:
        return jsonify(success=False, error="Unauthorized"), 401

    db = get_db()
    
    # Mark notification as seen (only for current user's notifications)
    cur = db.execute(
        "UPDATE notifications SET seen = 1 WHERE id = ? AND receiver_id = ?",
        (notif_id, user["id"])
    )
    db.commit()
    
    # Verify the update was successful
    # (rowcount may not be reliable, so we check the actual state)
    changed = db.execute("SELECT COUNT(1) AS cnt FROM notifications WHERE id = ? AND seen = 1", (notif_id,)).fetchone()["cnt"]
    db.close()

    if not changed:
        return jsonify(success=False, error="Not found or not allowed"), 404
    return jsonify(success=True)

@api.route("/delete_account_api", methods=["POST"])
def delete_account():
    current = current_user()
    if not current:
        # Not authenticated
        return jsonify({"error": "Not even authenticated"}), 401

    password = request.form.get("password", "")
    if not password:
        return jsonify({"error": "Password required"}), 400
    db = get_db()

    try:
        # Fetch the user row from DB (do not overwrite `current`)
        user_row = db.execute(
            "SELECT id, username, password FROM users WHERE username = ?",
            (current["username"],)
        ).fetchone()

        if not user_row:
            return jsonify({"error": "User not found"}), 404

        # Verify password hash
        if not check_password_hash(user_row["password"], password):
            # Don't reveal too much; flash if you want for UI
            flash("Incorrect password")
            return jsonify({"error": "Incorrect password"}), 403

        user_id = user_row["id"]
        db.execute("DELETE FROM comments WHERE user_id = ?;", (user_id,))
        db.execute("DELETE FROM dms WHERE sender_id = ?;", (user_id,))
        db.execute("DELETE FROM dms WHERE receiver_id = ?;", (user_id,))
        db.execute("DELETE FROM posts WHERE user_id = ?;", (user_id,))
        db.execute("DELETE FROM notifications WHERE receiver_id = ?;", (user_id,))

        db.execute("DELETE FROM users WHERE id = ?;", (user_id,))
        db.commit()
        redirect(url_for("main.login"))
        return redirect(url_for("main.index")), 200

    except sqlite3.IntegrityError as e:
        db.rollback() # FK constraint failed or other integrity issue
        return jsonify({"error": "Database constraint error", "detail": str(e)}), 500

    except Exception as e:
        db.rollback() # Generic server error — log server-side
        current_app.logger.exception("Error deleting account")
        return jsonify({"error": "Internal server error"}), 500

    finally:
        db.close()