from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.db.models import Q
from .models import Room, Topic, Message
from .forms import RoomForm, UserForm, ProfileUpdateForm

# Create your views here.



def home(request):
    # search q in user input
    q = request.GET.get('q') if request.GET.get('q') != None else '' #display all '' if q = none 
    # topic__name=q match user input with result
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) | #or 
        Q(name__icontains=q)|
        Q(description__icontains=q)
        ) #icontains: at least it contains what in q
    topics = Topic.objects.all()[0:5]
    room_count = rooms.count()
    room_messages = Message.objects.filter(
        Q(room__topic__name__icontains=q))[0:3] #only see activity to topic clicked ; q='' == all

    context = {'rooms' : rooms, 'topics' : topics, 'room_count' : room_count, 'room_messages':room_messages}
    return render(request, "base/home.html", context)

#==========
def LoginPage(request):
    #
    page = 'login'
    #one time login :
    if request.user.is_authenticated:
        return redirect('home')
    #
    if request.method == 'POST':
        username = request.POST.get('username').lower() #get user data from frontend [<input name="username"]
        password = request.POST.get('password')
        try: #check user exist
            user = User.objects.get(username=username)

        except:
            messages.error(request, "Login Failed,User does not exist")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # Redirect to a success page.
            return redirect('home')
        else:
            # Return an 'invalid login' error message.
            messages.error(request, "Username or password Not correct, Try again")
    context ={'page' : page}
    return render(request, "base/login_register.html", context)

def LogoutUser(request):
    logout(request) #delete token /user
    return redirect('home')

def RegisterPage(request):
    
    #page = 'register' {else} 
    form = UserCreationForm()
    context = {'form' : form}

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            return redirect('home')
        else:
            messages.error(request, 'An error occured during registration')


    return render(request, 'base/login_register.html', context)


#==========
def room(request, pk):   
    room = Room.objects.get(id=pk)
    #room messages :
    room_messages = room.message_set.all().order_by('-created') #query child related table, message model related by room, each room has messages
    participants = room.participants.all()

    if request.method == 'POST':
        message = Message.objects.create(
            user = request.user,
            room = room,
            body= request.POST.get('body'), #commentaires input name='body'
        )
        # add participant who have commented in room (from Post request)
        room.participants.add(request.user)
        return redirect('room', pk=room.id) #refresh


    context = {'room' : room, 'room_messages':room_messages, 'participants': participants}
    return render(request, "base/room.html", context)


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context={'user' : user, 'rooms':rooms, 
            'room_messages':room_messages,'topics':topics}
    
    return render(request, 'base/profile.html', context)


@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == "POST":
        topic_name = request.POST.get('topic')
        #updated or created / created true or false
        topic, created = Topic.objects.get_or_create(name=topic_name)
        
        Room.objects.create(
            host=request.user,
            topic=topic,
            name= request.POST.get('name'),
            description= request.POST.get('description'),
        )

        """
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.host = request.user
            room.save()
            return redirect('home')
        """
    context = {'form' : form, 'topics' : topics}
    return render(request,"base/room_form.html", context)

@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk) #db match
    form = RoomForm(instance=room)  #data pre fill
    
    if request.user != room.host: #only user can edit/update acess data
        return Httpresponse('Not Allowed')
    
    if request.method == "POST":
        topic_name = request.POST.get('topic')
        #updated or created / created true or false
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = request.POST.get('topic')
        room.description = request.POST.get('description')
         
        room.save()
         
        return redirect('home')

       # form = RoomForm(request.POST, instance=room)  #replace room value
        #if form.is_valid():
        #   form.save()
        #    return redirect('home')

    context = {'form' : form, 'room' : room}
    return render(request,"base/room_form.html", context)

@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    if request.user != room.host:
        return Httpresponse('Not Allowed')
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, "base/delete.html", {'obj' :room})


#===================
#Delete Messages : 
@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)
    if request.user != message.user:
        return Httpresponse('Not Allowed')
    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request, "base/delete.html", {'obj' :message})



@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)
    # Update profile form
    profile_form = ProfileUpdateForm(instance=user.profile)  # Initialize profile form with user's profile instance
    
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=user.profile)
        if form.is_valid() and profile_form.is_valid():
            form.save()
            profile_form.save()
            return redirect('user-profile', pk=user.id)  
    
    context={'form' : form, 'profile_form' : profile_form}

    return render(request, 'base/update-user.html', context)



def topicsPage(request):
    q = request.GET.get("q") if request.GET.get('q') != None else '' 
    topics = Topic.objects.filter(name__icontains=q)
    context={'topics': topics}
    return render(request, 'base/topics.html', context)




def activityPage(request):
    room_messages = Message.objects.all().order_by('-created')
    context = {'room_messages' : room_messages}
    return render(request, 'base/activity.html', context)


