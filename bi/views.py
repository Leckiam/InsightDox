from django.shortcuts import render

# Create your views here.
urlBase="bi/body/"
def home(request):
    return render(request,urlBase+'index.html')