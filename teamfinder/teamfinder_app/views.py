from django.shortcuts import render, redirect

# Create your views here.
def homepage(request):
    return redirect('/about')

def about(request):
    return render(request, 'about.html')