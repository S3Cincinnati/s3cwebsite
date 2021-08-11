from django.shortcuts import render
from django.http import HttpResponse
from .forms import GolfForm
from django.contrib.staticfiles.storage import staticfiles_storage
import csv

# Create your views here.
def home(request):

    # context = {'form':form}
    context = {}
    return render(request, 'custAdmin/home.html', context)

def golf_view(request):

    # context = {'form':form}
    context = {'golf_outing':process_data_by_event_date_code()}

    return render(request, 'custAdmin/golf.html', context)

def new_golf_classic_request(request):

    if request.method == 'POST':
        
        form_results = dict(request.POST)
        form_results.pop('csrfmiddlewaretoken')
    

        print(form_results)


    # form = GolfForm()
    context = {}
    return render(request, 'custAdmin/form.html', context)


def process_data_by_event_date_code():
    golf_main_context = []
    url_main = staticfiles_storage.path('golf_data/golf.csv')
    url_event_schedule = staticfiles_storage.path('golf_data/event_schedule.csv')

    with open(url_main, newline='') as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter='|', quotechar='|')
        for row in spamreader:
            d_row = dict(row)
            golf_main_context += [d_row]
    return golf_main_context
    