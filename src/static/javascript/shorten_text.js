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
