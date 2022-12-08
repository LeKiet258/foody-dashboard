from django.http import HttpResponse
from django.shortcuts import render, redirect
from dashboard.models import Vendor
from django.core.paginator import Paginator
from .models import *
from underthesea import word_tokenize

# Create your views here.
def select(request):
    res = Vendor.objects.all()
    for r in range(len(res)):
        cui = ''
        temp = res[r].cuisines[1:len(res[r].cuisines)-1].split(", ")
        for t in temp:
            t = t[1:len(t)-1].split('Món ')[-1]
            cui += t + ', '
        res[r].cuisines = cui[:-2]

        res[r].AvgScore = round(res[r].AvgScore, 1)

        res[r].min_price = int(res[r].min_price)
        res[r].max_price = int(res[r].max_price)
        res[r].TotalViews = int(res[r].TotalViews)
        if res[r].seeding_pct == '':
            res[r].seeding_pct = 0
        elif res[r].seeding_pct == '1.00':
            res[r].seeding_pct = 100
        else:
            if len(res[r].seeding_pct.split('.')[1]) == 1:
                res[r].seeding_pct = int(res[r].seeding_pct.split('.')[1])*10
            else:
                res[r].seeding_pct = int(res[r].seeding_pct.split('.')[1])

    paginator = Paginator(res, 25)  # Show 25 res per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    if request.method == 'POST':
        search = request.POST.get('search')
        searchPares = word_tokenize(search)

        finalVendors = []
        for searchPare in searchPares:
            for vendor in res:
                if searchPare.lower() in vendor.Name.lower() and vendor not in finalVendors:
                    finalVendors.append(vendor)

        context = {'vendors': finalVendors}

        if len(finalVendors) == 0:
            return render(request, 'search/emptyPage.html', context)

        else:
            # tạm thời chưa cho phân trang.
            paginator = Paginator(finalVendors, len(finalVendors))
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)

            return render(request, 'select.html', {'page_obj': page_obj})

    return render(request, 'select.html', {'page_obj': page_obj})