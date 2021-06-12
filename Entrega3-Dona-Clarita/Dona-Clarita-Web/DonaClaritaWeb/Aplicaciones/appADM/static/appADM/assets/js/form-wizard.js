(function ($) {
  'use strict';
  $(".style2-wizard").steps({
    headerTag: "h3",
    bodyTag: "div",
    autoFocus: true,
    titleTemplate: '<span class="number"></span> #title#',
    labels: {
      current: "",
      finish: 'Continuar',
      next: 'Siguiente',
      previous: 'Anterior'
    },
    onFinished: function (event, currentIndex) {
      if (!$("#form").valid()) {
        Swal.fire({
          title: "Ups!",
          text: "Ha ocurrido un error, revisa los campos",
          icon: "error",
          toast: true,
          position: "top-right", //bottom-left, bottom-right
          timer: 5000,
          timerProgressBar: true
        })
        return;
      }
      $("#form").submit();
    }
  });

})(jQuery);