from django.http import HttpResponse
from django.shortcuts import render, redirect
from dashboard.models import Vendor


# Create your views here.


def search(request):
    context = {}
    if request.method == 'POST':
        search = request.POST.get('search')

        vendors = Vendor.objects.all()

        finalVendors = []
        for vendor in vendors:
            if search.lower() in vendor.Name:
                finalVendors.append(vendor)

        context = {'vendors': finalVendors}
        # sử lý sự kiên search

        if len(finalVendors) == 0:
            return render(request, 'search/emptyPage.html', context)

        return render(request, 'search/searchResult.html', context)

    return render(request, 'search/searchPage.html', context)


def filter(request):
    context = {}

    return render(request, 'search/filter.html', context)
