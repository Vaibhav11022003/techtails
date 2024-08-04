from django.forms import ModelForm
from django.contrib.auth.models import User
from .models import Room,Message,Bio

class RoomForm(ModelForm):
    class Meta:
        model=Room
        fields='__all__'
        exclude=['host','participants']

class MessageForm(ModelForm):
    class Meta:
        model=Message
        fields='__all__'
        exclude=['user','room']

class UserForm(ModelForm):
    class Meta:
        model=User
        fields=['username','email']

class BioForm(ModelForm):
    class Meta:
        model=Bio
        fields=['bio','avatar']