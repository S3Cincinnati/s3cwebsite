from django.shortcuts import render
from django.http import HttpResponse
from .forms import GolfForm
from django.contrib.staticfiles.storage import staticfiles_storage
import csv
from datetime import date

from PIL import Image  
import PIL  

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
        print(form_results)
        proccess_golf_data(form_results, request.FILES)
        process_golf_images(form_results['full_date'][0], request.FILES)


    # form = GolfForm()
    context = {}
    return render(request, 'custAdmin/form.html', context)

def edit_golf_classic_request(request, key):

    if request.method == 'POST':
        
        form_results = dict(request.POST)
        form_results.pop('csrfmiddlewaretoken')
    

        proccess_golf_data(form_results, request.FILES)
        process_golf_images(form_results['full_date'][0], request.FILES)


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

def proccess_golf_data(golf_dict, files):

    # print(golf_dict)

    year_key = golf_dict['full_date'][0]
    f_date = date.fromisoformat(year_key)

    url_main = staticfiles_storage.path('golf_data/golf.csv')
    # image_url = staticfiles_storage.path('images/golf/' + str(f_date.year) + '/')

    content = []
    with open(url_main, newline='') as csvfile:
        golf_reader = csv.DictReader(csvfile, delimiter='|', quotechar='|')
        for row in golf_reader:
            d_row = dict(row)
            content += [d_row]

    content = {x['year_key']:x for x in content}

    
    event_images = []
    sponsor_images = []

    for im in files:
        if 'event' in im:
            event_images += ['/static/images/golf/' + str(f_date.year) + '/' + files[im].name]
        elif 'sponsor' in im:
            sponsor_images += ['/static/images/golf/' + str(f_date.year) + '/' + files[im].name]
            # picture = Image.open(files[im])  
            # picture.save(temp_url)

    content.update({year_key:{
        'year_key':year_key,
        'golf_course':golf_dict['golf_course'][0],
        'description':golf_dict['description'][0].replace('\r\n','%&'),
        'event_images':event_images,
        'sponsor_images':sponsor_images
        }})

    with open(url_main, 'w', newline='') as csvfile:
        fieldnames = ['year_key', 'golf_course', 'description', 'event_images','sponsor_images']

        writer = csv.DictWriter(csvfile, delimiter='|', fieldnames=fieldnames)
        writer.writeheader()
        
        writer.writerows([content[x] for x in content.keys()])

def process_golf_images(date_key, image_list):
    print(date_key)
    f_date = date.fromisoformat(date_key)
    url_main = staticfiles_storage.path('images/golf/' + str(f_date.year) + '/')
    
    for im in image_list:
        if 'event' in im or 'sponsor' in im:
            temp_url = url_main + '/' + image_list[im].name
            picture = Image.open(image_list[im])  
            picture.save(temp_url)

    # TODO - save to csv -> date_key|category (event or sponsor)|file_location