from django.shortcuts import render

# Create your views here.

def test_base(request):
    return render(request, 'poulets_app/base.html')
def dashboard(request):
    return render(request, 'poulets_app/base.html')