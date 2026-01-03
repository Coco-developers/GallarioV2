
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

// Uploading
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