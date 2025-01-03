$(document).ready(function() {
    $('.select').formSelect();
    autocomplete('remite','/persona/autocomplite/','Buscar Remitente...');
    autocomplete('consignado','/persona/autocomplite/','Buscar Consignado...');

    /*$('select[name="remite"]').select2({
        ajax: {
            delay: 250,
            type: 'GET',
            url: '/persona/autocomplite/',
            data: function(params){
                var queryParameters = {
                    term : params.term,
                    action : 'autocomplete'
                }
                return queryParameters
            },
            processResults: function(data){
                return { results : data}
            }

        }, 
        placeholder: 'Buscar Remitente',
        theme: "classic",
        language:"es",
        minimumInputLength: 3,
        //allowClear: true

    });

    $('select[name="consignado"]').select2({
        ajax: {
            delay: 250,
            type: 'GET',
            url: '/persona/autocomplite/',
            data: function(params){
                var queryParameters = {
                    term : params.term,
                    action : 'autocomplete'
                }
                return queryParameters
            },
            processResults: function(data){
                return { results : data}
            }

        }, 
        placeholder: 'Buscar Consignado',
        theme: "classic",
        language:"es",
        minimumInputLength: 3,
        //allowClear: true

    });
    */
    
});

