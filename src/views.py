from django.shortcuts import render
from django.http import HttpResponse
import csv
from django.contrib.staticfiles.storage import staticfiles_storage

# Create your views here.
def home(request):
    context = {}
    return render(request, 'src/home.html',context)

def get_golf_outing(request, year):

    context = {}
    context.update(process_data_by_event_date_code(year))
    
    return render(request, 'src/golf_classic.html',context)

def process_data_by_event_date_code(date_code):
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
        'year':date_code[0:4],
        'course':golf_main_context['golf_course'],
        'date_str':golf_main_context['full_date'],
        'descr': golf_main_context['description'].split(';'),
        'schedule':schedule
        }