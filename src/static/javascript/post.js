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