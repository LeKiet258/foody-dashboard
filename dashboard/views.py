from django.shortcuts import render
from django.http import HttpResponse
from .models import *
from django.core.paginator import Paginator

# Create your views here.

# def home(request):
# 	infor = Vendor.objects.all().count()
	
# 	return render(request, 'foody_dashboard/smallfood.html', {'infor': infor})


def home(request):
    res = Vendor.objects.all()
    paginator = Paginator(res, 25) # Show 25 res per page.

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

	#review = Vendor.objects.get()

    return render(request, 'foody_dashboard/smallfood.html', {'page_obj': page_obj})
