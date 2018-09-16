from django.shortcuts import render, redirect, HttpResponse
from .models import *
from django.conf import settings

from .dejavu import dejavu
from .dejavu import decoder



# Create your views here.


def index(request):
    if request.method == 'POST':
        music = request.FILES['data']
        save_url = settings.MEDIA_ROOT + "/music"
        music_name = '%s/%s' %(save_url, music.name)
        with open(music_name, 'wb') as f:
            for fdata in music.chunks():
                f.write(fdata)
        messgae = "上传成功"

        djv = dejavu.Dejavu()
        reconiger = dejavu.Recognizer(djv)
        song_list = djv.get_fingerprinted_song()
        song = reconiger.recognize_file(music_name)
    else:
        messgae = "上传失败"
        song ="None"
        song_list ="None"
    return render(request, "dejavu/index.html", {"message": messgae,
                                                 "song_list":song_list, "song": song})
def test(request):

    return HttpResponse("OK")



