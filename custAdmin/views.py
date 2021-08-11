from django.shortcuts import render
from django.http import HttpResponse
from .forms import GolfForm

# Create your views here.
def home(request):

    if request.method == 'POST':
        form = GolfForm(request.POST)
        if form.is_valid():

            name = form.cleaned_data['name']
            description = form.cleaned_data['description']

            print(name, description)
    form = GolfForm()
    context = {'form':form}
    return render(request, 'custAdmin/form.html', context)


def new_golf_classic_request(request):

    if request.method == 'POST':
        # form = GolfForm(request.POST)
        # if form.is_valid():

            # name = form.cleaned_data['name']
        description = request.POST['description']

        print(dict(request.POST))#, description)


    # form = GolfForm()
    context = {}
    return render(request, 'custAdmin/form.html', context)