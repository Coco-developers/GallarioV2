document.addEventListener('DOMContentLoaded', () => {
  if (Post) {PostStuff()};
  shortenText();
});
function shortenText() {
  const maxLength = 80; // number of characters to show initially
  posts = document.querySelectorAll('.post-text');

  posts.forEach(post => {
    post.style.display = 'block'; // makes it visible
    const fullText = post.textContent.trim();

    if (fullText.length > maxLength) {
      const shortText = fullText.slice(0, maxLength) + '...';

      // Create elements
      const shortSpan = document.createElement('span');
      shortSpan.className = 'short-text';
      shortSpan.textContent = shortText;

      const fullSpan = document.createElement('span');
      fullSpan.className = 'full-text';
      fullSpan.textContent = fullText;
      fullSpan.style.display = 'none';

      const readMore = document.createElement('span');
      readMore.className = 'read-more';
      readMore.textContent = '\n[Read More]';
      readMore.style.color = "blue";
	  readMore.style.cursor = "pointer";
	  readMore.addEventListener("mouseover", () => {
	    readMore.style.textDecoration = "underline";
	  });
	  readMore.addEventListener("mouseout", () => {
	    readMore.style.textDecoration = "none";
	  });
    readMore.style.fontStyle = 'italic';
      readMore.addEventListener('click', () => {
        if (fullSpan.style.display === 'none') {
          fullSpan.style.display = 'inline';
          shortSpan.style.display = 'none';
          readMore.textContent = ' [Read Less]';
        } else {
          fullSpan.style.display = 'none';
          shortSpan.style.display = 'inline';
          readMore.textContent = '\n[Read More]';
        }
		
      });

      // Clear original text and append new elements
      post.textContent = '';
      post.appendChild(shortSpan);
      post.appendChild(fullSpan);
      post.appendChild(readMore);
    }
  });
}
function PostStuff(){
        const updateCounts = (postId, likeCount, dislikeCount) => {
            document.getElementById(`like-count-${postId}`).textContent = likeCount;
            document.getElementById(`dislike-count-${postId}`).textContent = dislikeCount;
        };

        document.querySelectorAll('.like-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                e.preventDefault();
                const postId = btn.getAttribute('data-id');
                const res = await fetch(`/like/${postId}`, { method: 'POST' });
                const data = await res.json();
                if (data.success) updateCounts(postId, data.like_count, data.dislike_count);
            });
        });

        document.querySelectorAll('.dislike-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                e.preventDefault();
                const postId = btn.getAttribute('data-id');
                const res = await fetch(`/dislike/${postId}`, { method: 'POST' });
                const data = await res.json();
                if (data.success) updateCounts(postId, data.like_count, data.dislike_count);
            });
        });
    /**
     * Front-end "time ago" updater for elements with class="timestamp".
     * - Supports formats: "YYYY-MM-DD HH:MM:SS",   "YYYY-MM-DDTHH:MM:SS(.sss)(Z|±hh:mm)", or numeric epoch.
     * - If your server timestamps are in UTC but lack a 'Z', set assumeUTC =   true (see note).
     */
}
// deleting a post
function deletePost(postId, shouldConfirm = true) {
  if (shouldConfirm) {
    if (!confirm("Do you want to continue with deleting this post? (This cannot be undone)")) {
      return; // user canceled
    }
  }

  // Create a form dynamically to send POST request
  const form = document.createElement("form");
  form.method = "POST";
  form.action = `/delete/${postId}`;  // matches your backend route

  document.body.appendChild(form);
  form.submit();
}
// on the main page, for for selecting what should be choosen for sorting
function applySort() {
  const sortby = document.getElementById("sortby").value;
  const accending = document.getElementById("order").value;

  if (sortby == null || ascending == null) {
    return;
  }
  const params = new URLSearchParams(window.location.search);
  params.set("sortby", sortby);
  params.set("accending", accending);

  window.location.search = params.toString(); // reloads page with updated query
}

//index.html stuff
document.addEventListener('DOMContentLoaded', () => {
  async function updateCounters(url, postId) {
    try {
      const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const data = await res.json();

      if (data.success) {
        // Update counts
        const likeCount = document.getElementById(`like-count-${postId}`);
        const dislikeCount = document.getElementById(`dislike-count-${postId}`);

        if (likeCount) likeCount.textContent = data.like_count ?? 0;
        if (dislikeCount) dislikeCount.textContent = data.dislike_count ?? 0;

        // Update button states visually
        const likeBtn = document.querySelector(`.like-btn[data-id="${postId}"]`);
        const dislikeBtn = document.querySelector(`.dislike-btn[data-id="${postId}"]`);

        if (data.user_liked !== undefined) {
          likeBtn.classList.toggle('active', data.user_liked);
        }

        if (data.user_disliked !== undefined) {
          dislikeBtn.classList.toggle('active', data.user_disliked);
        }
      } else {
        console.warn('Server returned failure:', data);
      }
    } catch (err) {
      console.error('Error updating counters:', err);
    }
  }

  // Like buttons
  document.querySelectorAll('.like-btn').forEach((btn) => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const postId = btn.dataset.id;
      updateCounters(`/like/${postId}`, postId);
    });
  });

  // Dislike buttons
  document.querySelectorAll('.dislike-btn').forEach((btn) => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const postId = btn.dataset.id;
      updateCounters(`/dislike/${postId}`, postId);
    });
  });
});
