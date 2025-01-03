enviar_ose = (pk)=>{
    //e.preventDefault();
    Swal.fire({
        title: 'Desea Emitir Comprobante?'+pk,
        showCancelButton: true,
        confirmButtonText: 'Si',
        cancelButtonText: `No`,
        showLoaderOnConfirm: true,
        preConfirm: async () => {
            return fetch(`/facturacion/enviar/ose/${pk}`)
            .then(response => {
                console.log(response)
                if (!response.ok) {
                throw new Error(response.statusText)
                }
                return response.json()
            })
            .catch(error => {
                Swal.showValidationMessage(
                `Request Fallado: ${error}`
                )
            })
        },
        allowOutsideClick: () => !Swal.isLoading()
      }).then((result) => {
        console.log(result)
        if (result.isConfirmed) {
          Swal.fire('Se acreado con exito!', '', 'success')

        } 
      })
}

descargar_excel = (evt)=>{
    evt.preventDefault();
    form_ose = document.getElementById('form-descarga-excel')
    form_ose.submit();

}

