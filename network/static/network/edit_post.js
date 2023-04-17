function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        let cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            let cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.edit-button').forEach(function(button) {
        button.onclick = function() {
            let postId = button.dataset.post;
            let postContentElement = document.querySelector(`#post-content-${postId}`);
            let postContent = postContentElement.innerHTML.trim();

            let textarea = document.createElement('textarea');
            textarea.id = `textarea-${postId}`;
            textarea.className = 'form-control';
            textarea.value = postContent;

            let saveButton = document.createElement('button');
            saveButton.innerHTML = 'Save';
            saveButton.className = 'btn btn-primary';

            let cancelButton = document.createElement('button');
            cancelButton.innerHTML = 'Cancel';
            cancelButton.className = 'btn btn-secondary';

            cancelButton.onclick = function() {
                postContentElement.innerHTML = postContent;
                textarea.remove();
                saveButton.remove();
                cancelButton.remove();
                button.style.display = 'block';
            };

            saveButton.onclick = function() {
                let newContent = textarea.value.trim();
                if (newContent && newContent !== postContent) {
                    // Save the updated content
                    console.log('Saving updated content:', newContent);
                    fetch(`/edit_post/${postId}`, {
                        method: 'POST',
                        body: JSON.stringify({
                            content: newContent
                        }),
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCookie('csrftoken')
                        }
                    })
                    .then(response => response.json())
                    .then(data => {
                        console.log('Received data:', data);
                        postContentElement.innerHTML = data.content;
                    });
                }
                textarea.remove();
                saveButton.remove();
                cancelButton.remove();
                button.style.display = 'block';
            };

            postContentElement.innerHTML = '';
            postContentElement.appendChild(textarea);
            postContentElement.appendChild(cancelButton);
            postContentElement.appendChild(saveButton);

            button.style.display = 'none';
        };
    });
});
