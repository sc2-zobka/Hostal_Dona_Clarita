

$("#form").validate({
    rules:{
        fdesde:{
            required: true,
        },
        fhasta:{
            required: true,
        },
        accesorios:{
            required: false
        },          
        nhuesped:{
          required:true,    
          number:true,
          minlength:1,
          maxlength:2           
        }
    },
    messages:{
        fdesde:{
            required:  "Campo Obligatorio. Completalo para continuar. Ej: 01/05/2021",
        },
        fhasta:{
            required:  "Campo Obligatorio. Completalo para continuar. Ej: 01/05/2021",
        },
        nhuesped:{
            required:  "Campo Obligatorio. Completalo para continuar. Ej: 1",          
        },        
             
        accesorios:{
            required:  "Campo Obligatorio. Seleccione una opción para Continuar",
        },        
               
    }

})







