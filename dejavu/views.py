from django.shortcuts import render, redirect, HttpResponse
from .models import *
from django.conf import settings

from .dejavu import dejavu
from .dejavu import recognize
from .dejavu import database
from .dejavu import decoder



# Create your views here.


def index(request):
    if request.method == 'POST':
        music = request.FILES['data']
        save_url = settings.MEDIA_ROOT + "/music"
        data_url = settings.MEDIA_ROOT + "/mp3"
        music_name = '%s/%s' %(save_url, music.name)
        with open(music_name, 'wb') as f:
            for fdata in music.chunks():
                f.write(fdata)
        messgae = "上传成功"
        djv = dejavu.Dejavu()
        #djv.fingerprint_directory(data_url, ['.mp3'])
        reconiger = recognize.Recognizer(djv)
        song_list = djv.get_song_list()
        song = reconiger.recognize_file(music_name)
        song_name = song['song_name']
    else:
        messgae = "上传失败"
        song_name ="None"
        song_list ="None"
    return render(request, "dejavu/index.html", {"message": messgae,
                                                 "song_list":song_list, "song": song_name})
def test(request):
    djv = dejavu.Dejavu()
    data_url = settings.MEDIA_ROOT + "/mp3"
    djv.fingerprint_directory(data_url, ['.wav'])

    return HttpResponse("OK")



