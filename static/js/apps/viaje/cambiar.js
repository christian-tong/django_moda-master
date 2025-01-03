let datos={}
rutas = ()=>{
    // GET AJAX request
    $.ajax({
        type: 'GET',
        url: window.location.pathname,
        dataType:"json",
        success: function (response) {
            // if not valid user, alert the user
            console.log(response)
            datos=response
        },
        error: function (response) {
            console.log(response)
        }
    })
    return datos
}

asientos = (data)=>{
    
    console.log(data.value)
    $.ajax({
        type: 'GET',
        url: window.location.pathname+"?idprograma="+data.value,
        //dataType:"json",
        success: function (response) {
            $('#model_carro').html(response)
        },
        error: function (response) {
            console.log(response)
        }
    });
}

$(document).ready(function() { 
      

    $('#example').DataTable( {
        'searching':false,
        'paging': false,
        ajax: rutas(),
        columns: [
            { data: "id" },
            { data: "nombreViaje" },
            { data: "fechaViaje" },
            { data: "horaViaje" },
            { data: "horaViaje" },
        ],
        columnDefs: [
            { 
                targets: [-1],
                visible: true,
                orderable:false,
                render: function(data,type,row){
                    return `<p>
                    <label>
                      <input name="programacionViaje" type="radio" value="${row.id}" onclick="asientos(this)"" />
                      <span>Seleccionar</span>
                    </label>
                  </p>`
                }
            },
        ],
        "language": {
            "url": "//cdn.datatables.net/plug-ins/9dcbecd42ad/i18n/Spanish.json"
        }
    } );

    $('select').formSelect();
    $('#id_numAsiento').val('')

    $('.pasadiso').empty();

    $('.libre').click(function(){

        let asiento = $(this).attr('asiento');
        let idasiento = $(this).attr('idasiento')

        $('#id_idasiento').val(idasiento)
        $("#id_numAsiento").val(asiento)
        
    });


    

})
