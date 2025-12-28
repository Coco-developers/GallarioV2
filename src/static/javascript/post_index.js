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

/**
 * Front-end "time ago" updater for elements with class="timestamp".
 * - Supports formats: "YYYY-MM-DD HH:MM:SS",   "YYYY-MM-DDTHH:MM:SS(.sss)(Z|±hh:mm)", or numeric epoch.
 * - If your server timestamps are in UTC but lack a 'Z', set assumeUTC =   true (see note).
 */

const assumeUTC = true; // <-- set true if your server timestamps are UTC    but have no timezone marker

function parseTimestamp(ts) {
  if (!ts) return null;
  // If it's a number (epoch seconds or ms)
  if (!isNaN(ts)) {
    // use numeric value; try to decide seconds vs ms (>=1e12 => ms)
    const n = Number(ts);
    return n > 1e12 ? new Date(n) : new Date(n * 1000);
  }

  // Trim and normalize
  ts = String(ts).trim();

  // If it's like "YYYY-MM-DD HH:MM:SS" -> convert to "YYYY-MM-DDTHH:MM:SS"
  // Browsers reliably parse "YYYY-MM-DDTHH:MM:SS" as local time, and     "YYYY-MM-DDTHH:MM:SSZ" as UTC.
  const spaceDateTime = /^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(?:\.\d+)?$/;
  if (spaceDateTime.test(ts)) {
    let iso = ts.replace(' ', 'T');
    if (assumeUTC) iso += 'Z';
    return new Date(iso);
  }

  // If it's ISO-ish but missing Z and you want to assume UTC, add Z
  const isoNoTZ = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?$/;
  if (isoNoTZ.test(ts) && assumeUTC) {
    return new Date(ts + 'Z');
  }

  // Otherwise let Date try to parse (handles ISO with timezone)
  const d = new Date(ts);
  return isNaN(d.getTime()) ? null : d;
}

function timeAgo(date, now = new Date()) {
  if (!date) return '';
  let seconds = Math.floor((now - date) / 1000);
  if (seconds < 0) seconds = 0;

  if (seconds < 10) return 'just now';
  if (seconds < 60) return `${seconds} second${seconds !== 1 ? 's' : ''}  ago`;

  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes} min${minutes !== 1 ? 's' : ''} ago`;

  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours} hour${hours !== 1 ? 's' : ''} ago`;

  const days = Math.floor(hours / 24);
  if (days === 1) return 'yesterday';
  if (days < 30) return `${days} day${days !== 1 ? 's' : ''} ago`;

  const months = Math.floor(days / 30);
  if (months < 12) return `${months} month${months !== 1 ? 's' : ''} ago`;

  const years = Math.floor(months / 12);
  return `${years} year${years !== 1 ? 's' : ''} ago`;
}

function updateTimestamps() {
  const nodes = document.querySelectorAll('.timestamp');
  const now = new Date();
  nodes.forEach(node => {
    // Save original raw value in data-original if not already set
    if (!node.dataset.original) node.dataset.original = node.textContent. trim();

    const raw = node.dataset.original;
    const dt = parseTimestamp(raw);
    const pretty = dt ? timeAgo(dt, now) : raw; // fall back to raw if    parse fails
    node.textContent = pretty;
    // keep full timestamp visible on hover
    node.title = raw;
  });
}

// initial run
updateTimestamps();
// refresh every 60 seconds so "mins ago" stays accurate
setInterval((updateTimestamps), 60 * 1000);

// Post uploading feedback
document.getElementById('post-upload')?.addEventListener('submit', function() {
  const submitButton = this.querySelector('button[type="submit"]');
  if (submitButton) {
    submitButton.disabled = true;
    submitButton.textContent = 'Your post is being uploaded...';
  }
});

// Image preview before upload
const photoInput = document.getElementById("photoInput");
const imagePreview = document.getElementById("imagePreview");

photoInput.addEventListener("change", () => {
    const file = photoInput.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = e => {
        imagePreview.src = e.target.result;
        imagePreview.classList.remove("hidden");
    };
    reader.readAsDataURL(file);
});

// Status bar
const form = document.getElementById("post-upload");
const progressContainer = document.getElementById("progressContainer");
const progressBar = document.getElementById("progressBar");
const progressText = document.getElementById("progressText");

form.addEventListener("submit", function (e) {
    e.preventDefault();

    const formData = new FormData(form);
    const xhr = new XMLHttpRequest();

    xhr.open("POST", form.action, true);

    xhr.upload.onprogress = function (e) {
        if (e.lengthComputable) {
            const percent = Math.round((e.loaded / e.total) * 100);
            progressContainer.classList.remove("hidden");
            progressBar.style.width = percent + "%";
            progressText.textContent = percent + "%";
        }
    };

    xhr.onload = function () {
        if (xhr.status === 200) {
            progressText.textContent = "Upload complete ✅";
            progressBar.classList.add("bg-green-500");
            setTimeout(() => {
              location.reload();
            }, 200);
        } else {
            progressText.textContent = "Upload failed ❌";
            progressBar.classList.add("bg-red-500");
        }
    };

    xhr.send(formData);
});