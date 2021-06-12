from django import forms
from django.contrib.auth.forms import UserCreationForm
from Aplicaciones.app.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ["email", "username",
                  "password1", "password2"]

class CustomEmpleadoCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        self.fields['password1'].required = False
        self.fields['password2'].required = False
        # If one field gets autocompleted but not the other, our 'neither
        # password or both password' validation will be triggered.
        self.fields['password1'].widget.attrs['autocomplete'] = 'off'
        self.fields['password2'].widget.attrs['autocomplete'] = 'off'
        
    class Meta:
        model = User
        fields = ["email", "username"]
        exclude = ['password1' , 'password2']