from django.shortcuts import render

# Create your views here.
def hello(request):
    return render(request, 'homepage/index.html')

def aboutme(request):
    return render(request, 'homepage/aboutme.html')
