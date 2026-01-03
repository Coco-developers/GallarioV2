
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