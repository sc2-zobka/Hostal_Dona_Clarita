$("#myForm").validate({
    rules:{
        act_pwd:{
            required: true,
            minlength:8,
            maxlength:20
        },
        new_pwd:{
            required: true,
            minlength:8,
            maxlength:20
        },        
        conf_new_pwd:{
            required: true,
            minlength:8,
            maxlength:20
        },
                                
    },
   

})







