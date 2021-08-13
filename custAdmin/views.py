from django.shortcuts import render
from django.http import HttpResponse
from .forms import GolfForm
from django.contrib.staticfiles.storage import staticfiles_storage
import csv
from datetime import date

# Create your views here.
def home(request):

    # context = {'form':form}
    context = {}
    return render(request, 'custAdmin/home.html', context)

def golf_view(request):

    # context = {'form':form}
    context = {'golf_outing':get_event_data()}

    return render(request, 'custAdmin/golf.html', context)

def new_golf_classic_request(request):

    if request.method == 'POST':
        
        form_results = dict(request.POST)
        form_results.pop('csrfmiddlewaretoken')
    

        f_date = date.fromisoformat(form_results['full_date'][0])
        print(f_date.day, f_date.month, f_date.year, f_date.weekday())
        #proccess_golf_data(form_results)


    # form = GolfForm()
    context = {}
    return render(request, 'custAdmin/form.html', context)

def edit_golf_classic_request(request, key):

    if request.method == 'POST':
        
        form_results = dict(request.POST)
        form_results.pop('csrfmiddlewaretoken')
    

        proccess_golf_data(form_results)


    outing_data = get_data_by_event_date_code(key)
    outing_data['descr'] = '\r\n'.join(outing_data['descr'])
    print(outing_data)
    context = {'data':outing_data}
    return render(request, 'custAdmin/form.html', context)



def get_event_data():
    golf_main_context = []
    url_main = staticfiles_storage.path('golf_data/golf.csv')
    url_event_schedule = staticfiles_storage.path('golf_data/event_schedule.csv')

    with open(url_main, newline='') as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter='|', quotechar='|')
        for row in spamreader:
            d_row = dict(row)
            golf_main_context += [d_row]
    return golf_main_context
    

def get_data_by_event_date_code(date_code):
    
    golf_main_context = {}
    url_main = staticfiles_storage.path('golf_data/golf.csv')
    url_event_schedule = staticfiles_storage.path('golf_data/event_schedule.csv')

    with open(url_main, newline='') as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter='|', quotechar='|')
        for row in spamreader:
            d_row = dict(row)
            if date_code in d_row['year_key']:
               golf_main_context = d_row
    
    events = []
    with open(url_event_schedule, newline='') as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter='|', quotechar='|')
        for row in spamreader:
            d_row = dict(row)
            if date_code in d_row['key']:
               events += [d_row]

    schedule = {}
    for e in events:
        key = e['full_date'] + '_' + e['location']
        if key not in schedule.keys():
            schedule.update({key:{
                'date':e['full_date'],
                'location':e['location'],
                'events':[]
            }})

        schedule[key]['events'] += [{
            'time':e['time'],
            'description':e['description'],
        }]

    schedule = [schedule[x] for x in schedule.keys()]

    return {
        'course':golf_main_context['golf_course'],
        'date':golf_main_context['year_key'],
        'descr': golf_main_context['description'].split('%&'),
        'schedule':schedule
        }

def proccess_golf_data(golf_dict):

    url_main = staticfiles_storage.path('golf_data/golf.csv')
    content = []
    with open(url_main, newline='') as csvfile:
        golf_reader = csv.DictReader(csvfile, delimiter='|', quotechar='|')
        for row in golf_reader:
            d_row = dict(row)
            content += [d_row]
    

    print(content)

    content = {x['year_key']:x for x in content}

    
    content.update({'20180512':{
        'year_key':'20180512', 
        'full_date':golf_dict['full_date'][0],
        'golf_course':golf_dict['golf_course'][0],
        'description':golf_dict['description'][0].replace('\r\n','%&')
        }})

    print(content)

    with open(url_main, 'w', newline='') as csvfile:
        fieldnames = ['year_key', 'full_date', 'golf_course', 'description']

        writer = csv.DictWriter(csvfile, delimiter='|', fieldnames=fieldnames)
        writer.writeheader()
        
        writer.writerows([content[x] for x in content.keys()])