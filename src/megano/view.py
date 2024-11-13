from django.shortcuts import render


def footer(request):
    return render(request, 'footer.html')

def footer_about(request):
    return render(request, 'footer-about-item.html')

def header_top(request):
    return render(request, 'header-top.html')

def header_main(request):
    return render(request, 'header-main.html')

def header_search(request):
    return render(request, 'header-search.html')

def index(request):
    return render(request, 'index.html')