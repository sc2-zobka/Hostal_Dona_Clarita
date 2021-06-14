

$("#form1").validate({
    rules:{
        tip_hab:{
            required: true,
        },        
        nro_hab:{
            required: true,
            minlength:1,
            maxlength:5
        },
        precio:{
            required:true,
            number:true,
            minlength:1,
            maxlength:9  
        },
        disponibilidad:{
            required: true,
        }, 
        muestra_menu:{
            required: true,
        },
        descripcion:{
            required: true,
            minlength:5,
            maxlength:100
        },
        imagen:{
            required: true,
        },        
    },
    messages:{
        tip_hab:{
            required:  "Campo Obligatorio. Seleccione una Opción para Continuar",        
        },         
        nro_hab:{
            required:  "Campo Obligatorio. Completalo para continuar. ",
        },        
        precio:{
            required:  "Campo Obligatorio. Completalo para continuar. ",
        },
        disponibilidad:{
            required:  "Campo Obligatorio. Seleccione una Opción para Continuar",        
        },    
        muestra_menu:{
            required:  "Campo Obligatorio. Seleccione una Opción para Continuar",        
        },             
        descripcion:{
            required:  "Campo Obligatorio. Completalo para continuar. ",
        }, 
        imagen:{
            required:  "Campo Obligatorio. Seleccione una Imagen para Continuar",        
        },                 
    }

})







