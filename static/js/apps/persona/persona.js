var elems = document.querySelectorAll('select');
var instances = M.FormSelect.init(elems);

let search = document.querySelector(".search");
let tipDocum = document.querySelector("select[name='tipoDoc']");


visiblePersona = ()=>{
    
    let text =tipDocum.options[tipDocum.selectedIndex].text
    
    let personajuridica=document.getElementById('personajuridica')
    let personanatural=document.getElementById('personanatural')

    personajuridica.style.display = 'none';
    personanatural.style.display = "block"

    if(text =='RUC' ){       

        personajuridica.style.display = "block"
        personanatural.style.display = "none"
        return false
    }
}

visiblePersona()

tipDocum.addEventListener('change',(e)=>{    
    e.preventDefault();
    visiblePersona()   

});

search.addEventListener('click',(e)=>{
    e.preventDefault();
    document.getElementById('preload').classList.toggle('hide')
    let numDoc = document.querySelector("input[name='numDoc']").value
    let crcxf = document.querySelector("input[name='csrfmiddlewaretoken']").value
    let tipDoc = document.querySelector("select[name='tipoDoc']")
    let direccion = document.querySelector("input[name='direccion']")
    tipDoc = tipDoc.options[tipDoc.selectedIndex].text

    let data = {}
    
    if(tipDoc =='DNI' && numDoc.length==8){
        data = { tipodoc: tipDoc, numdoc: numDoc}
    }
    else if(tipDoc == 'RUC' && numDoc.length==11){
        data = { tipodoc: tipDoc, numdoc: numDoc}
    }
    else{
        alert("Solo se acepta DNI=8 dígitos y RUC=11 dígitos ");
        return false;
    }    

    postData('/persona/buscar/api/doc', data)
    .then(data => {

        if(tipDoc =='RUC'){
            document.getElementById('preload').classList.toggle('hide')
            let denominacion = document.querySelector("input[name='denominacion']")
            denominacion.value = data.denominacion
            direccion.value = data.direccion

            document.querySelector("label[for='id_denominacion']").className = "active"
            document.querySelector("label[for='id_direccion']").className = "active"
        }
        else{
            document.getElementById('preload').classList.toggle('hide')
            let nombres = document.querySelector("input[name='nombres']")
            let apellidoP = document.querySelector("input[name='apellidoP']")
            let apellidoM = document.querySelector("input[name='apellidoM']")
            let fechaNac = document.querySelector("input[name='fechaNac']")
            let genero = document.querySelector("select[name='genero']")

            nombres.value = data.nombres
            apellidoP.value = data.apellido_paterno
            apellidoM.value = data.apellido_materno
            fechaNac.value = data.fecha_nacimiento
            /* //genero.options[value=data.sexo].setAttribute("selected","")
            for(let i=0; i<genero.length;i++){
                if(genero.options[i].value == data.sexo) genero.options[i].setAttribute("selected","")
            }*/            
            direccion.value = data.direccion
            

            document.querySelector("label[for='id_nombres']").className = "active"
            document.querySelector("label[for='id_apellidoP']").className = "active"
            document.querySelector("label[for='id_apellidoM']").className = "active"
            document.querySelector("label[for='id_direccion']").className = "active" 
        }
        
        

    });
    
});


