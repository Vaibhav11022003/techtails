from django.shortcuts import render,redirect
from django.db.models import Q
from .models import Room,Topic,Message,Bio
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import RoomForm,MessageForm,UserForm,BioForm
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.forms import UserCreationForm

def loginPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method=='POST':
        username=request.POST.get('username').lower()
        password=request.POST.get('password')
        try:
            user=User.objects.get(username=username)
        except:
            messages.error(request,'user not exist...')
        user=authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect('home')
        else :
            messages.error(request,'username or password does not exist...')

    context={
        'page':'login',
    }
    return render(request,'base/login_register.html',context)

def registerPage(request):
    form =UserCreationForm()
    if request.method=='POST':
        form=UserCreationForm(request.POST)
        if form.is_valid():
            user=form.save(commit=False)
            user.username=user.username.lower()
            user.save()
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,'an error occured while registration...')
    context={
        'page':'register',
        'form':form,
    }
    return render(request,'base/login_register.html',context)

def logoutPage(request):
    logout(request)
    return redirect('home')

def home(request):
    q=request.GET.get('q')
    if q==None:
        q=''
    rooms=Room.objects.filter(
        Q(topic__name__icontains=q) | 
        Q(name__icontains=q) |
        Q(desc__icontains=q)
        )
    room_messages=Message.objects.filter(room__in=rooms)
    topics=Topic.objects.all()
    context={
        'rooms':rooms,
        'topics':topics,
        'room_count':rooms.count(),
        'room_messages':room_messages,
    }
    return render(request,'base/home.html',context)

def room(request,pk):
    reqroom=None
    reqroom=Room.objects.get(id=int(pk))
    room_messages=reqroom.message_set.all()
    participants=reqroom.participants.all()

    if request.method=="POST":
        message=Message.objects.create(
            room=reqroom,
            user=request.user,
            body=request.POST.get('body')
            )
        reqroom.participants.add(request.user)
        return redirect('room',pk=reqroom.id)
    context={
        'room':reqroom,
        'room_messages':room_messages,
        'participants':participants,
    }
    return render(request,'base/room.html',context)

def userProfile(request,pk):
    user=User.objects.get(id=int(pk))
    rooms=user.room_set.all()
    room_messages=user.message_set.all()
    topics=Topic.objects.all()
    context={
        'user':user,
        'rooms':rooms,
        'room_messages':room_messages,
        'topics':topics,
    }
    return render(request,'base/profile.html',context)

@login_required(login_url='login')
def createRoom(request):
    form=RoomForm()
    topics=Topic.objects.all()
    if request.method=='POST':
        topic_name=request.POST.get('topic')
        topic,created=Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            desc=request.POST.get('desc'),
        )
        return redirect('home')
    context={'form':form,
             'topics':topics
             }
    return render(request,'base/room_form.html',context)

@login_required(login_url='login')
def updateRoom(request,pk):
    room=Room.objects.get(id=int(pk))
    topics=Topic.objects.all()
    prevtopic=room.topic
    form=RoomForm(instance=room)
    if request.user!=room.host:
        return redirect('home')
    if request.method=="POST":
        topic_name=request.POST.get('topic')
        topic,created=Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            desc=request.POST.get('desc'),
        )
        return redirect('home')
    context={'form':form,
             'topics':topics,
             'prevtopic':prevtopic,
             }
    return render(request,'base/room_form.html',context)

@login_required(login_url='login')
def deleteRoom(request,pk):
    room=Room.objects.get(id=int(pk))
    if request.user!=room.host:
        return redirect('home')
    if request.method=="POST":
        room.delete()
        return redirect('home')
    context={
        'obj':room,
    }
    return render(request,'base/delete.html',context)

def updateMessage(request,pk):
    message=Message.objects.get(id=int(pk))
    form=MessageForm(instance=message)
    if request.method=='POST':
        form=MessageForm(request.POST,instance=message)
        if form.is_valid():
            form.save()
            return redirect('room',message.room.id)
    context={
        'form':form,
        'message':message
    }
    return render(request,'base/message_form.html',context)

def deleteMessage(request,pk):
    try:
        message=Message.objects.get(id=int(pk))
    except:
        return redirect('home')
    if message.user!=request.user:
        return redirect('home')
    if request.method=="POST":
        message_cnt=request.user.message_set.filter(room=message.room).count()
        if message_cnt==1:
            message.room.participants.remove(request.user)
        message.delete()
        return redirect('home')
    context={
        'obj':message,
    }
    return render(request,'base/delete.html',context)

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import BioForm

@login_required(login_url='login')
def updateUser(request):
    # Create the form instance with the current user’s bio instance and request.FILES to handle file uploads
    if request.method == 'POST':
        form = BioForm(request.POST, request.FILES, instance=request.user.bio)
        if form.is_valid():
            form.save()
            return redirect('profile', request.user.id)
    else:
        form = BioForm(instance=request.user.bio)

    context = {
        'form': form,
        'bio': request.user.bio
    }
    return render(request, 'base/update-user.html', context=context)
