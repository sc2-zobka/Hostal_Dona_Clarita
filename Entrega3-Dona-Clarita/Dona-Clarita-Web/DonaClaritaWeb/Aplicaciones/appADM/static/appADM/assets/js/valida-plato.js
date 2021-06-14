

$("#form1").validate({
    rules:{
        comedor:{
            required: true,
        },        
        nombreplato:{
            required: true,
            minlength:1,
            maxlength:40 
        },
        fdesde:{
            required: true,
            date: true
        }, 
        fhasta:{
            required: true,
            date: true
        }, 

                               
    },
    messages:{
        comedor:{
            required:  "Campo Obligatorio. Seleccione un Tipo para Continuar. ",
        },        
        nombreplato:{
            required:  "Campo Obligatorio. Ingresa el Nombre del Plato para Continuar ",
        },
        fdesde:{
            required:  "Campo Obligatorio. Selecciona una Fecha de Inicio",
        },       
        fhasta:{
            required:  "Campo Obligatorio. Selecciona una Fecha de Termino",
        },                 
    
   
    }

})







