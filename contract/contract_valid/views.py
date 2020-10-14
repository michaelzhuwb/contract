from django.shortcuts import render

# Create your views here.
def login(request):
    """查看所有学科"""
    return render(request, 'login.html',)