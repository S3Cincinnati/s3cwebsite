from django.shortcuts import render
from django.http import HttpResponse
from .forms import GolfForm
from django.contrib.staticfiles.storage import staticfiles_storage
import csv
from datetime import date

from PIL import Image  
import PIL  
import os

from .git_publishing.git_publish_all import git_publish_all, git_clone

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
        # print(f_date.day, f_date.month, f_date.year, f_date.weekday())
        # print(form_results)
        git_clone()

        proccess_golf_data(form_results, request.FILES)
        process_golf_images(form_results['full_date'][0], request.FILES)

        git_publish_all()

    # form = GolfForm()
    context = {}
    return render(request, 'custAdmin/form.html', context)

def edit_golf_classic_request(request, key):

    if request.method == 'POST':
        
        form_results = dict(request.POST)
        form_results.pop('csrfmiddlewaretoken')

        git_clone()

        proccess_golf_data(form_results, request.FILES)
        process_golf_images(form_results['full_date'][0], request.FILES)

        git_publish_all()


    outing_data = get_data_by_event_date_code(key)
    outing_data['descr'] = '\r\n'.join(outing_data['descr'])
    print(outing_data)
    context = {'data':outing_data}
    return render(request, 'custAdmin/golf_form.html', context)


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
    golf_reg_context = []
    sponsor_reg_context = []

    if os.getenv('DJANGO_ENV','') == 'local':
        url_main = os.path.dirname(__file__) + '/../media/golf_data/'
    else:
        url_main = staticfiles_storage.path('golf_data')

    with open(url_main + '/golf.csv', newline='') as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter='|', quotechar='|')
        for row in spamreader:
            d_row = dict(row)
            if date_code in d_row['year_key']:
               golf_main_context = d_row

    
    with open(url_main + '/golf_registration.csv', newline='') as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter='|', quotechar='|')
        for row in spamreader:
            d_row = dict(row)
            if date_code in d_row['year_key']:
                d_row.update({'display_count':int(d_row['count']) + 1})
                golf_reg_context += [d_row]

    with open(url_main + '/sponsor_registration.csv', newline='') as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter='|', quotechar='|')
        for row in spamreader:
            d_row = dict(row)
            if date_code in d_row['year_key']:
                d_row.update({'display_count':int(d_row['count']) + 1})
                sponsor_reg_context += [d_row]
    
    events = []
    with open(url_main + '/event_schedule.csv', newline='') as csvfile:
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
        'schedule':schedule,
        'golf_registration':golf_reg_context,
        'golf_option_count':len(golf_reg_context),
        'sponsor_registration':sponsor_reg_context,
        'sponsor_option_count':len(sponsor_reg_context)
        }

def proccess_golf_data(golf_dict, files):

    print(golf_dict)

    year_key = golf_dict['full_date'][0]
    f_date = date.fromisoformat(year_key)

    if os.getenv('DJANGO_ENV','') == 'local':
        url_write_backup = os.path.dirname(__file__) + '/../media/golf_data/'
    else:
        url_write_backup = os.path.dirname(__file__) + '/git_publishing/deploy/media/golf_data/'

    content = []
    with open(url_write_backup + 'golf.csv', newline='') as csvfile:
        golf_reader = csv.DictReader(csvfile, delimiter='|', quotechar='|')
        for row in golf_reader:
            d_row = dict(row)
            content += [d_row]

    content = {x['year_key']:x for x in content}

    golf_option_title = list(filter(lambda x: ('golf_option_title_' in x), golf_dict.keys()))
    stripe_price_variable_price_input_golf = list(filter(lambda x: ('stripe_price_variable_price_input_golf_' in x), golf_dict.keys()))
    golf_option_textarea = list(filter(lambda x: ('golf_option_textarea_' in x), golf_dict.keys()))

    golf_registrations = [{
            'year_key':year_key,
            'golf_option_title':golf_dict[golf_option_title[x]][0],
            'stripe_price_variable':golf_dict[stripe_price_variable_price_input_golf[x]][0],
            'golf_option_textarea':golf_dict[golf_option_textarea[x]][0],
            'count':x
        } for x in range(len(golf_option_textarea))]


    sponsor_option_title = list(filter(lambda x: ('sponsor_option_title_' in x), golf_dict.keys()))
    stripe_price_variable_input_sponsor = list(filter(lambda x: ('stripe_price_variable_input_sponsor_' in x), golf_dict.keys()))
    sponsor_option_textarea = list(filter(lambda x: ('sponsor_option_textarea_' in x), golf_dict.keys()))

    sponsor_registrations = [{
            'year_key':year_key,
            'sponsor_option_title':golf_dict[sponsor_option_title[x]][0],
            'stripe_price_variable':golf_dict[stripe_price_variable_input_sponsor[x]][0],
            'sponsor_option_textarea':golf_dict[sponsor_option_textarea[x]][0],
            'count':x
        } for x in range(len(sponsor_option_title))]
    

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

    for link in [url_write_backup]:
        with open(link + 'golf.csv', 'w', newline='') as csvfile:
            fieldnames = ['year_key', 'golf_course', 'description', 'event_images','sponsor_images']

            writer = csv.DictWriter(csvfile, delimiter='|', fieldnames=fieldnames)
            writer.writeheader()
            
            writer.writerows([content[x] for x in content.keys()])
        
        with open(link + 'golf_registration.csv', 'w', newline='') as csvfile:
            fieldnames = ['year_key', 'golf_option_title', 'stripe_price_variable', 'golf_option_textarea','count']

            writer = csv.DictWriter(csvfile, delimiter='|', fieldnames=fieldnames)
            writer.writeheader()
            
            writer.writerows(golf_registrations)

        with open(link + 'sponsor_registration.csv', 'w', newline='') as csvfile:
            fieldnames = ['year_key', 'sponsor_option_title', 'stripe_price_variable', 'sponsor_option_textarea','count']

            writer = csv.DictWriter(csvfile, delimiter='|', fieldnames=fieldnames)
            writer.writeheader()
            
            writer.writerows(sponsor_registrations)

def process_golf_images(date_key, image_list):

    f_date = date.fromisoformat(date_key)

    # url_main = staticfiles_storage.path('images/golf/' + str(f_date.year) + '/')
    if os.getenv('DJANGO_ENV','') == 'local':
        url_write_backup = os.path.dirname(__file__) + '../media/images/golf/' + str(f_date.year) + '/'
    else:
        url_write_backup = os.path.dirname(__file__) + '/git_publishing/deploy/media/images/golf/' + str(f_date.year) + '/'

    for link in [url_write_backup]:
        
        
        for im in image_list:
            if 'event' in im or 'sponsor' in im:
                temp_url = link + '/' + image_list[im].name
                picture = Image.open(image_list[im])  
                picture.save(temp_url)

    # TODO - save to csv -> date_key|category (event or sponsor)|file_location