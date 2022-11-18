from django.shortcuts import render, redirect
from django.http import HttpResponse

# Create your views here.


def search(request):
    context = {}
    if request.method == 'POST':
        search = request.POST.get('search')
        print(search)
        return redirect('result')

    return render(request, 'search/searchPage.html', context)


def result(request):
    stores = []
    context = {}

    # if len(stores) == 0:
    #     return render(request, 'search/emptyPage.html', context)

    return render(request, 'search/searchResult.html', context)
