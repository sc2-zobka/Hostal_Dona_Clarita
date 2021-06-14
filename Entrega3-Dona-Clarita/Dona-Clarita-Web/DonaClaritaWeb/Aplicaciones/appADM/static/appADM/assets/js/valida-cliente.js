

$("#form1").validate({
    rules:{
        username:{
            required: true,
        },        
        rut:{
            required: true,
        },
        r_social:{
            required: true,
            minlength:3,
            maxlength:50
        },
        fono:{
            number:true,
            minlength:8,
            maxlength:9  
        },
        email:{
            required: true,
            email: true
        }, 
        direccion:{
            required: true,
            minlength:3,
            maxlength:50
        },
        password1:{
            required: true,
            minlength:8,
            maxlength:20
        },
        password2:{
            required: true,
            minlength:8,
            maxlength:20            
        },        
        reg_sel:{
            required: true,
        },        
        com_sel:{
            required: true,
        },                                
    },
    messages:{
        username:{
            required:  "Campo Obligatorio. Completalo para continuar. ",
        },        
        rut:{
            required:  "Campo Obligatorio. Completalo para continuar. Ej: 11111111-1 ",
        },
        r_social:{
            required:  "Campo Obligatorio. Completalo para continuar. Ej: Doña Clarita SPA ",
        },       
        email:{
            required:  "Campo Obligatorio. Completalo para continuar. Ej: correo@dominio.cl",
        },                 
        direccion:{
            required:  "Campo Obligatorio. Completalo para continuar. Ej: Av. Grecia 1243",
        },        
        reg_sel:{
            required:  "Campo Obligatorio. Seleccione una Región para Continuar",        
        }, 
        com_sel:{
            required:  "Campo Obligatorio. Seleccione una Comuna para Continuar",        
        },         
    }

})







