// Reset avatar
document.getElementById("avatarInput").value = '';

async function saveDescription() {
    const desc = document.getElementById("descriptionTextarea").value;
    try {
        let response = await fetch("/description", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ description: desc })
        });

        if (response.ok) {
            document.getElementById("profileDescription").textContent = desc;
        } else {
            alert("Failed to update description.");
        }
    } catch (err) {
        console.error("Error:", err);
        alert("Something went wrong.");
    }
}

document.getElementById("descriptionTextarea").addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
        event.preventDefault(); // stop form submission if inside a form
        document.getElementById("descriptionSave").click(); // trigger the click
    }
});

function ChangeDescription() {
    document.getElementById('descriptionControls')?.classList.add('hidden');
    document.getElementById('descriptionEditor')?.classList.remove('hidden');
    const ta = document.getElementById('descriptionTextarea');
    if (ta) ta.focus();
}

function CancelDescription() {
    document.getElementById('descriptionEditor')?.classList.add('hidden');
    document.getElementById('descriptionControls')?.classList.remove('hidden');
}
  // Avatar input filename preview
document.getElementById('avatarInput')?.addEventListener('change', function (e) {
    const file = e.target.files && e.target.files[0];
    if (file) {
        document.getElementById('avatarFilename').textContent = file.name;
    } else {
        document.getElementById('avatarFilename').textContent = '';
    }
});


async function deletePost(postId) {
    if (!confirm("Delete this post?")) return;

    try {
        const res = await fetch(`/delete/${postId}`, {
            method: "POST",
            credentials: "same-origin", // REQUIRED for Flask login session
            headers: {
                "X-Requested-With": "XMLHttpRequest"
            }
        });

    if (!res.ok) {
        throw new Error("Delete failed");
    } else {
        location.reload();
    }

    } catch (err) {
        console.error(err);
        alert("Could not delete post.");
    }
}
// For one button avatar changing
const saveAvatarButton = document.getElementById("SaveAvatar");
const AvatarInput = document.getElementById("avatarInput");
saveAvatarButton.addEventListener('click', e => {
    if (AvatarInput.value == '') {
        AvatarInput.click();
    }
});
AvatarInput.addEventListener("change", () => {
    if (AvatarInput.value == ''){ 
        saveAvatarButton.innerText = "Change Avatar"; 
    } else{
        saveAvatarButton.innerText = "Apply Avatar"; 
    }
});

