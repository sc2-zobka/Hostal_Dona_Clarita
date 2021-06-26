

$("#form1").validate({
    rules:{
        nombre:{
            required: true,
        },        
        precio:{
            required: true,
            number: true,
            minlength:1,
            maxlength:6 
        },
        descripcion:{
            required: true,
            minlength:5,
            maxlength:50 
        }, 
    },
    messages:{
      
        nombre:{
            required:  "Campo Obligatorio. Ingresa el Nombre del Servicio Adicional para Continuar ",
        },
        precio:{
            required:  "Campo Obligatorio. ",
        },       
        descripcion:{
            required:  "Campo Obligatorio. Ingrese una descripción para Continuar",
        },                 
    
   
    }

})







