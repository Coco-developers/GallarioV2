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