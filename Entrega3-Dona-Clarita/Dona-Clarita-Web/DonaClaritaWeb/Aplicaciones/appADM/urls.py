from django.urls import path
from Aplicaciones.appADM.views import login_new, registro,config_user,pass_user, config_emp, config, tipo_moneda, edit_tipo_moneda
urlpatterns = [
    path('login/', login_new, name="login_new"),
    path('registro/', registro, name="registro"),

    path('dashboard/config-user/', config_user, name="config-user"),
    path('dashboard/pass-user/', pass_user, name="pass-user"),
    path('dashboard/config/', config_emp, name="config-emp"),


    #***Módulo:Empleados*** Opción: configuraciones empresa
    path('dashboard/config-empresa/', config, name="config"),
    path('dashboard/tipo-moneda/', tipo_moneda, name="tipo-moneda"),
    path('dashboard/edit-tipo-moneda/<id>/', edit_tipo_moneda, name="edit-tipo-moneda"),

]