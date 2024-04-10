
from django.contrib.auth.models import  User #AbstractUser
from django.db import models







#custom user (add image profile..)
#

'''
class User(AbstractUser):
    name = models.CharField(max_length=200, null=True)
    email = models.EmailField(unique=True, null=True)
    bio = models.TextField(null=True)
    # avatar for user image upload
    avatar = models.ImageField(null=True, default="avatar.svg")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    # Add custom fields here
    #profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    # Add other custom fields as needed  

'''


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True,blank=True)

    def __str__(self):
        return self.user.username


# Create your models here.

class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name





class Room(models.Model):
    #User host (connected also to messages by room)
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True) 
    
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True) #if topic is deleted ,room still exist!!
    name= models.CharField(max_length=200)
    description = models.TextField(null=True, blank = True)
    # participant : Many to many field
    participants = models.ManyToManyField(User, related_name='participants', blank=True)
    #below : auto fill
    updated = models.DateTimeField(auto_now=True) # everytime updated
    created = models.DateTimeField(auto_now_add=True) #never change timestamp

    
    class Meta:
        ordering = ['-updated', '-created'] #order by last updated and created / -
    def __str__(self):
        return self.name


#each room gonna have messages : 
class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)   #when deleteing user, message will be deleted!   
    #room one to many relationship :
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True) # everytime updated
    created = models.DateTimeField(auto_now_add=True) #never change timestamp, creation date 

    class Meta:
        ordering = ['-updated', '-created'] #order by last updated and created / -

    def __str__(self):
        return self.body[0:50]

  