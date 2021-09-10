from typing import Text
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

from itertools import groupby
import ast

# Create your views here.
def home(request):

    context = {}
    return render(request, 'custAdmin/home.html', context)

def edit_home(request):

    if request.method == 'POST':
        
        form_results = dict(request.POST)
        form_results.pop('csrfmiddlewaretoken')

        git_clone()

        process_home_data(form_results)

        git_publish_all()

    context = get_home_data()
    print(context)

    return render(request, 'custAdmin/home_form.html', context)

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
    # print(outing_data)
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
    
def key_func(k):
    return k['event_day']

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
            if date_code in d_row['year_key']:
                events += [d_row]

    schedule = {'total':0,'data':[], 'child_sizes':[]}
    count = 0
    for key, value in groupby(events, key_func):
        date_obj = date.fromisoformat(key)
        data = list(value)
        c1 = 0
        for item in data:
            item.update( {"count":c1})
            c1 += 1

        schedule['data'] += [{
            'date':key,
            'location':' ' if len(data) == 0 else data[0]['location'],
            'data':data,
            'count':count}]
        count += 1
    schedule['total'] = len(schedule['data'])
    schedule['child_sizes'] = [ len(x['data']) for x in schedule['data']]

    # print(schedule)
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

    # print(golf_dict)

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
            'golf_option_title':golf_dict[golf_option_title[x]][0].strip(),
            'stripe_price_variable':golf_dict[stripe_price_variable_price_input_golf[x]][0].strip(),
            'golf_option_textarea':golf_dict[golf_option_textarea[x]][0].strip(),
            'count':x
        } for x in range(len(golf_option_textarea))]


    sponsor_option_title = list(filter(lambda x: ('sponsor_option_title_' in x), golf_dict.keys()))
    stripe_price_variable_input_sponsor = list(filter(lambda x: ('stripe_price_variable_input_sponsor_' in x), golf_dict.keys()))
    sponsor_option_textarea = list(filter(lambda x: ('sponsor_option_textarea_' in x), golf_dict.keys()))

    sponsor_registrations = [{
            'year_key':year_key,
            'sponsor_option_title':golf_dict[sponsor_option_title[x]][0].strip(),
            'stripe_price_variable':golf_dict[stripe_price_variable_input_sponsor[x]][0].strip(),
            'sponsor_option_textarea':golf_dict[sponsor_option_textarea[x]][0].strip(),
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
        'golf_course':golf_dict['golf_course'][0].strip(),
        'description':golf_dict['description'][0].replace('\r\n','%&').strip(),
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

        with open(link + 'event_schedule.csv', 'w', newline='') as csvfile:
            fieldnames = ['year_key', 'event_day','location', 'time', 'description']

            writer = csv.DictWriter(csvfile, delimiter='|', fieldnames=fieldnames)
            writer.writeheader()
            
            writer.writerows(process_schedule(golf_dict,year_key))

def process_schedule(golf_dict, year_key):
    keys = list(filter(lambda x: ('day_' in x), golf_dict.keys()))
    schedule = {}
    days = {}
    locations = {}
    
    print(keys)
    for k in keys:
        k_new = k[k.find('_')+1:]
        day_num = k_new[:k_new.find('_')]
        
        if len(day_num) == 0 and k_new not in schedule.keys():
            schedule.update({k_new:{}})
            days.update({k_new:golf_dict[k][0]})

        if len(day_num) > 0:
            k_new = k_new[k_new.find('_')+1:] # removes day_
            k_new = k_new[k_new.find('_')+1:] # removes event_
            
            num = k_new[:k_new.find('_')]
            k_new = k_new[k_new.find('_')+1:]

            if day_num == 'location':
                locations.update({k_new:golf_dict[k][0]})
            else:
                if num not in schedule[day_num].keys():
                    schedule[day_num].update({num:{}})
                    schedule[day_num][num].update({'date':golf_dict[k][0]})
                if len(num) != 0:
                    schedule[day_num][num].update({k_new:golf_dict[k][0]})
    
 
    s1 = []
    for d in schedule.keys():
        day = []
        events = schedule[d]
        for e in events.keys():
            day += [{'year_key':year_key, 'event_day':days[d],'location':locations[d],'time':schedule[d][e]['time'], 'description':schedule[d][e]['description']}]
        s1 += day
            
    return s1

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

def get_home_data():
    data = {'blocks':[]}
    if os.getenv('DJANGO_ENV','') == 'local':
        url_main = os.path.dirname(__file__) + '/../media/static_page_data/'
    else:
        url_main = staticfiles_storage.path('static_page_data')

    with open(url_main + '/home.csv', newline='') as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter='|', quotechar='|')
        for row in spamreader:
            d_row = dict(row)
            if 'count_vals' == d_row['format']:
                donations_arr = {'key':'count_vals','vals':ast.literal_eval(d_row['text'])}
                count = 0
                for d in donations_arr['vals']:
                    d.update({'count':count})
                    count += 1
                data['blocks'] += [donations_arr]
                print(data['blocks'][-1])
            elif 'two_pic_frame' == d_row['format']:
                images = ast.literal_eval(d_row['images'])
                titles = ast.literal_eval(d_row['titles'])
                text = ast.literal_eval(d_row['text'])
                
                # print(images, titles[0], text)/
                # data['blocks'] += [{'key':'two_pic_frame','image_1':images[0], 'image_2':images[1], 'title':titles[0], 'text':text}]
            elif 'golf_outing' == d_row['format']:
                images = ast.literal_eval(d_row['images'])
                titles = ast.literal_eval(d_row['titles'])
                text = ast.literal_eval(d_row['text'])
                
                # print(images, titles[0], text)
                # t = 'Join us at S3C\'s ' + titles[0] + ' Annual fundraising golf outing'

                # data['blocks'] += [{'key':'two_pic_frame','img1':images[0], 'img2':images[0], 'title':t, 'text':text}]
                # data['blocks'] += [{'key':'golf_outing','flier':, 'outing_number':titles[0], 'date':titles[1],'text':text}]
    return data

def process_home_data(home_dict):

    if os.getenv('DJANGO_ENV','') == 'local':
        url_write_backup = os.path.dirname(__file__) + '/../media/static_page_data/'
    else:
        url_write_backup = os.path.dirname(__file__) + '/git_publishing/deploy/media/static_page_data/'

    donation_data = {'text':{},'val':{}}

    # {'donation_text_0': ['Cancer Research'], 'donation_value_0': ['$43,620.00'], 'donation_text_1': ['Family Support'], 'donation_value_1': ['$145,482.00']}
    for d in home_dict.keys():
        temp_d = d
        if 'donation_' in temp_d:
            temp_d = temp_d.replace('donation_', '')
            if 'text_' in temp_d:
                temp_d = temp_d.replace('text_', '')
                donation_data['text'].update({temp_d:home_dict[d][0]})
            elif 'value_' in temp_d:
                temp_d = temp_d.replace('value_', '')
                donation_data['val'].update({temp_d:home_dict[d][0]})

    rows = []
    
    donations = []
    for i in range(len(donation_data['text'])):
        donations += [{'text':donation_data['text'][str(i)], 'val':donation_data['val'][str(i)]}]

    rows += [{'titles':[], 'text':donations, 'images':[], 'format':'count_vals'}]

    with open(url_write_backup + 'home.csv', 'w', newline='') as csvfile:
        fieldnames = ['titles', 'text','images', 'format']

        writer = csv.DictWriter(csvfile, delimiter='|', fieldnames=fieldnames)
        writer.writeheader()
        
        writer.writerows(rows)
