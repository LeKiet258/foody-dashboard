from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.


def search(request):
    context = {}
    return render(request, 'search/searchPage.html', context)


def result(request):
    context = {}
    return render(request, 'search/searchResult.html', context)
