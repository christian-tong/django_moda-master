$(document).ready(function() {
    $('.select').formSelect();
    autocomplete('remite','/persona/autocomplite/','Buscar Remitente...');
    autocomplete('consignado','/persona/autocomplite/','Buscar Consignado...');
    
});

