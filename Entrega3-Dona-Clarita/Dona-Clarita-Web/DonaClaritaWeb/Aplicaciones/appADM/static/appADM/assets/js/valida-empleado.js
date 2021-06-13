

$("#form1").validate({
    rules:{
        nombre:{
            required: true,
            minlength:3,
            maxlength:50
        },  
        apellido_p:{
            required: true,
            minlength:3,
            maxlength:50
        }, 
        apellido_m:{
            required: false,
            minlength:3,
            maxlength:50
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
        fec_nac:{
            date: true
        }, 
        tipo_e:{
            required: true,
        },                
        direccion:{
            required: true,
            minlength:3,
            maxlength:50
        },
        reg_sel:{
            required: true,
        },
        com_sel:{
            required: true,
        },                                
    },
    messages:{
        nombre:{
            required:  "Campo Obligatorio. Completalo para continuar. Ej: Juan ",
        },  
        apellido_p:{
            required:  "Campo Obligatorio. Completalo para continuar. Ej: Gonzalez ",
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
        tipo_e:{
            required:  "Campo Obligatorio. Seleccione una Opción para Continuar",        
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







