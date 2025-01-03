
autocomplete = (name,url,label,filt = null)=>{
    return $(`select[name="${name}"]`).select2({
        ajax: {
            delay: 250,
            type: 'GET',
            url: url,
            data: function(params){
                var queryParameters = {
                    term : params.term,
                    action : 'autocomplete',
                    filtro : filt
                }
                return queryParameters
            },
            processResults: function(data){
                return { results : data}
            },
    
        }, 
        placeholder: label,
        theme: "classic",
        language:"es",
        minimumInputLength: 3,
        
        //allowClear: true
    
    });
};

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

//'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val()
//'X-CSRFToken': getCookie('csrftoken'),

async function postData(url = '', data = {}) {

    const response = await fetch(url, {
      method: 'POST', // *GET, POST, PUT, DELETE, etc.
      credentials: 'same-origin', // include, *same-origin, omit
      headers: {
        'X-CSRFToken': getCookie('csrftoken'),
        'Content-Type': 'application/json'
        // 'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: JSON.stringify(data) // body data type must match "Content-Type" header
    });
    return response.json(); // parses JSON response into native JavaScript objects
  }

  async function getData(url) {
    //let url = 'users.json';
    try {
        let res = await fetch(url);
        return await res.json();
    } catch (error) {
        console.log(error);
    }
}





  enviarForm = (event)=>{
    event.preventDefault()
    document.getElementById('preload').classList.toggle('hide')
    document.getElementById('btn-send').classList.toggle('disabled')
    event.target.submit()
}

