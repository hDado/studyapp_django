from django.forms import ModelForm
from .models import Room, Profile
from django.contrib.auth.models import User

#

class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = '__all__'
        exclude = ['host', 'participants']




class UserForm(ModelForm):
    class Meta:
        model=User
        fields=['username', 'email']



class ProfileUpdateForm(ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'avatar']

