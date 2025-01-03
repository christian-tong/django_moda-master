$(document).ready(function() {
    $('.select').formSelect();
    autocomplete('cliente','/persona/autocomplite/','Buscar Cliente...')
    .on('select2:select', function (e) { 
        console.log('select event '+ e);
        poblarSelect = document.querySelector('#poblarSelect')
        poblarSelect.innerHTML = `<p>
                                    Tipo doc : ${e.params.data.tipoDoc.descripcion}<br>
                                    Num doc : ${e.params.data.numDoc}<br>
                                    Direccion : ${e.params.data.direccion}
                                    </p>`
        /*for (const property in e.params.data.tipoDoc) {
            console.log(`${property}: ${e.params.data.tipoDoc[property]}`);
          }*/
    });
})
