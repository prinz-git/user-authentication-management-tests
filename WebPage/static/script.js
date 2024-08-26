 
 //should really do this with document.onload but who has the time
 document.addEventListener('DOMContentLoaded', function() {
    var modal = document.getElementById('signupModal');
    var link = document.getElementById('signupLink');
    var close = document.getElementsByClassName('close')[0];
    //avoid stupid null object issue when i'm in another page and there's no signup link
    if(modal){
        link.onclick = function() {
        modal.style.display = 'block';
        }
        
        close.onclick = function() {
        modal.style.display = 'none';
        }
        
        window.onclick = function(event) {
            if (event.target == modal) {
                modal.style.display = 'none';
            }
        }
    }
  });

  function deleteUser(userId) {
    fetch('/delete/' + userId, { method: 'POST' })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          location.reload();
        } else {
          //need to handle this better...some other time
          console.log(data.error);
        }
      })
      .catch(error => {
        console.log('An error occurred:', error);
      });
  }