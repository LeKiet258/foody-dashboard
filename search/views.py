from django.http import HttpResponse
from django.shortcuts import render, redirect
from dashboard.models import Vendor

from underthesea import word_tokenize


# Create your views here.


def search(request):
    context = {}
    if request.method == 'POST':
        search = request.POST.get('search')

        searchPares = word_tokenize(search)

        vendors = Vendor.objects.all()

        finalVendors = []
        for searchPare in searchPares:
            for vendor in vendors:
                if searchPare.lower() in vendor.Name.lower() and vendor not in finalVendors:
                    finalVendors.append(vendor)

        context = {'vendors': finalVendors}

        if len(finalVendors) == 0:
            return render(request, 'search/emptyPage.html', context)

        return render(request, 'search/searchResult.html', context)

    return render(request, 'search/searchPage.html', context)


def filter(request):
    context = {}

    return render(request, 'search/filter.html', context)
