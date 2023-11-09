import os
from chat.models import Chat
import speech_recognition as sr
from django.http import HttpResponse
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.shortcuts import render, redirect


def home(request):
    print("request: ", request)
    chats = Chat.objects.all()

    chats_list = list(chats.values())
    # create a Querryset
    #all_users = User.objects.filter(messages__isnull=False).distinct()
    all_users = User.objects.filter(id__in=chats.values_list('id', flat=True)) #all_users : <QuerySet [<User: doctor_1>, <User: speech_admin>]>
    all_users = User.objects.exclude(id=1) # Rajiv changed all_users to all_users : <QuerySet [<User: doctor_1>, <User: doctor_2>]> eliminating speech_admin
    #all_users = User.objects.filter(id=1).delete()
    print("all_users after eliminating User id 1 , speech_admin:", all_users)
    print("chat_list :",chats_list)


    # ctx = {
    #     'home': 'active',
    #     'chat': chats,
    #     'allusers': all_users
    # }
    
    ctx = {
       'home': 'active',
       'chat': chats,
       'allusers': all_users
    }
    
    if request.user.is_authenticated:
        return render(request, 'chat.html', ctx)
    else:
        return render(request, 'base.html', None)


def upload(request):
    customHeader = request.META['HTTP_MYCUSTOMHEADER']

    # obviously handle correct naming of the file and place it somewhere like media/uploads/
    filename = str(Chat.objects.count())
    filename = filename + "name" + ".wav"
    uploadedFile = open(filename, "wb")
    # the actual file is in request.body
    uploadedFile.write(request.body)
    uploadedFile.close()
    # put additional logic like creating a model instance or something like this here
    r = sr.Recognizer()
    harvard = sr.AudioFile(filename)
    with harvard as source:
        audio = r.record(source)
    msg = r.recognize_google(audio)
    os.remove(filename)
    chat_message = Chat(user=request.user, message=msg)
    print("chat_message :", chat_message)
    if msg != '':
        chat_message.save()
    return redirect('/')


def post(request):
    if request.method == "POST":
        msg = request.POST.get('msgbox', None)
        print('Our value = ', msg)
        chat_message = Chat(user=request.user, message=msg)
        if msg != '':
            chat_message.save()
        return JsonResponse({'msg': msg, 'user': chat_message.user.username})
    else:
        return HttpResponse('Request should be POST.')


def messages(request):
    chat = Chat.objects.all()
    return render(request, 'messages.html', {'chat': chat})
