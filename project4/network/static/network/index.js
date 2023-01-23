document.addEventListener('DOMContentLoaded', function() {    
    document.querySelectorAll('.content-view').forEach(element => {
        element.style.display = 'block';
        
        const id = element.dataset.post;
        const content = element.dataset.content;
        
        // Edit button only available for a user's own posts
        if (document.querySelector(`#edit-view-${id}`)) {
            const editBtn = document.createElement('button');
            editBtn.setAttribute('style', 'border: none; background-color: transparent; color: RoyalBlue; text-decoration: underline; padding: 0px;');

            editBtn.innerHTML = 'Edit';
            document.querySelector(`#content-view-${id}`).appendChild(editBtn);
            editBtn.addEventListener('click', () => editing(id, content));
        }
    });

    // Upon loading the page all editing textareas are hidden from view
    document.querySelectorAll('.edit-view').forEach(element => {
        element.style.display = 'none';
    });

    document.querySelectorAll('.likes').forEach(element => {
        const postID = element.dataset.value;
        const likeBtn = document.createElement('button');
        likeBtn.setAttribute('style', 'border: none; background-color: transparent;');

        let likeStatus = element.dataset.likestatus;
        const symbol = (likeStatus === '1' ? '&#x2764;' : '&#x2665;'); 

        likeBtn.innerHTML = symbol;
        document.querySelector(`#like-${postID}`).appendChild(likeBtn);

        likeBtn.addEventListener('click', () => like(postID, likeStatus));
    });
});

function editing(id, content) {
    // In order to edit a post the content view is hidden and replaced with the editing view
    document.querySelector(`#content-view-${id}`).style.display = 'none';
    document.querySelector(`#edit-view-${id}`).style.display = 'block';

    const saveBtn = document.createElement('button');
    saveBtn.setAttribute('class', 'btn btn-secondary btn-sm');
    saveBtn.setAttribute('type', 'submit');

    saveBtn.innerHTML = 'Save';
    document.querySelector(`#edit-form-${id}`).appendChild(saveBtn);

    // Prefill textarea with post content
    document.querySelector(`#edit-${id}`).value = content;

    document.querySelector(`#edit-form-${id}`).onsubmit = () => {
        const csrftoken = getCookie('csrftoken');
        const request = new Request(
            `/edit/${id}`,
            {headers: {'X-CSRFToken': csrftoken}}
        );
        fetch(request, {
            method: 'PUT',
            mode: 'same-origin',
            body: JSON.stringify({
                content: document.querySelector(`#edit-${id}`).value
            })
        }).then(() => {
            location.reload();
        })
        return false;
    };
}

function like(id, likeStatus) {
    likeStatus = !likeStatus;

    const csrftoken = getCookie('csrftoken');
    const request = new Request(
        `/like/${id}`,
        {headers: {'X-CSRFToken': csrftoken}}
    );
    fetch(request, {
        method: 'PUT',
        mode: 'same-origin',
        body: JSON.stringify({
            likes: document.querySelector(`#like-${id}`).dataset.user
        })
    }).then(() => {
        location.reload();
    })
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}