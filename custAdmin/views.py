from typing import Text
from django.shortcuts import redirect, render
from django.http import HttpResponse, FileResponse
from .forms import FoursomeRegistration, GolfForm
from django.contrib.staticfiles.storage import staticfiles_storage
import csv
from datetime import date

from PIL import Image  
import PIL  
import os

from .git_publishing.git_publish_all import git_publish_all, git_clone

from itertools import groupby
import ast

from src.models import *
import xlsxwriter

# Create your views here.
def home(request):

    context = {}
    return render(request, 'custAdmin/home.html', context)

# Organization Information
def edit_organiztion_information(request):
    if request.method == 'POST':
        
        form_results = dict(request.POST)
        form_results.pop('csrfmiddlewaretoken')

        git_clone()

        process_organization_info(form_results)

        git_publish_all()

    context = get_organization_information()

    return render(request, 'custAdmin/organization_information_form.html', context)
def process_organization_info(request):
    if os.getenv('DJANGO_ENV','') == 'local':
        url_write_backup = os.path.dirname(__file__) + '/../media/static_page_data/'
    else:
        url_write_backup = os.path.dirname(__file__) + '/git_publishing/deploy/media/static_page_data/'

    rows = [{'contact_email':request['contact_email'][0]}]

    with open(url_write_backup + 'organization_information.csv', 'w', newline='') as csvfile:
        fieldnames = ['contact_email']

        writer = csv.DictWriter(csvfile, delimiter='|', fieldnames=fieldnames)
        writer.writeheader()
        
        writer.writerows(rows)
def get_organization_information():
    if os.getenv('DJANGO_ENV','') == 'local':
        url_main = os.path.dirname(__file__) + '/../media/static_page_data/'
    else:
        url_main = staticfiles_storage.path('static_page_data')

    context = {'contact_email':''}
    with open(url_main + '/organization_information.csv', newline='') as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter='|', quotechar='|')
        for row in spamreader:
            context['contact_email'] = row['contact_email']

    return context

# Home Page
def edit_home(request):

    if request.method == 'POST':
        
        form_results = dict(request.POST)
        form_results.pop('csrfmiddlewaretoken')

        git_clone()

        process_home_data(form_results, request.FILES)

        git_publish_all()

    context = get_home_data()

    return render(request, 'custAdmin/home_form.html', context)
def process_home_data(home_dict, image_list):

    if os.getenv('DJANGO_ENV','') == 'local':
        url_write_backup = os.path.dirname(__file__) + '/../media/static_page_data/'
    else:
        url_write_backup = os.path.dirname(__file__) + '/git_publishing/deploy/media/static_page_data/'

    if os.getenv('DJANGO_ENV','') == 'local':
        image_path = os.path.dirname(__file__) + '/../media/images/home/'
    else:
        image_path = os.path.dirname(__file__) + '/git_publishing/deploy/media/images/home/'


    donation_data = {'text':{},'val':{}}
    golf_event = {'format':'golf_outing'}
    two_image_frames = {}
    left_text = {'titles':[],'text':[],'images':[],'format':'left_panel'}
    right_text = {'titles':[],'text':[],'images':[],'format':'right_panel'}
    irs_text = {'titles':[],'text':[],'images':[],'format':'irs_panel'}

    for d in home_dict.keys():
        print(d, home_dict[d])
        temp_d = d
        if 'donation_' in temp_d:
            temp_d = temp_d.replace('donation_', '')
            if 'text_' in temp_d:
                temp_d = temp_d.replace('text_', '')
                donation_data['text'].update({temp_d:home_dict[d][0]})
            elif 'value_' in temp_d:
                temp_d = temp_d.replace('value_', '')
                donation_data['val'].update({temp_d:home_dict[d][0]})
        if 'golf_event_' in temp_d:
            temp_d = temp_d.replace('golf_event_', '')
            if 'text' in temp_d:
                golf_event.update({'titles':home_dict[d]})
            if 'full_date' in temp_d:
                golf_event.update({'full_date':home_dict[d]})
            if 'description' in temp_d:
                text = [x.strip() for x in home_dict[d][0].split('\r\n')]
                golf_event.update({'text':text})
            if 'image_current' in temp_d:
               golf_event.update({'images':home_dict[d]})
               
        if 'two_pic_frame_' in temp_d:
            temp_d = temp_d.replace('two_pic_frame_', '')
            index = temp_d[-1]
            temp_d = temp_d.replace('_'+index, '')
            if index not in two_image_frames.keys():
                two_image_frames.update({index:{'format':'two_pic_frame','images':['','']}})
            
            if 'title' in temp_d:
                two_image_frames[index].update({'titles':home_dict[d]})
            if 'description' in temp_d:
                text = [x.strip() for x in home_dict[d][0].split('\r\n')]
                two_image_frames[index].update({'text':text})
            if 'image_left_current' in temp_d:
                two_image_frames[index]['images'][0] = home_dict[d][0]
            if 'image_right_current' in temp_d:
                two_image_frames[index]['images'][1] = home_dict[d][0]
        
        if 'left_text_' in temp_d:
            temp_d = temp_d.replace('left_text_', '')
            
            if 'title' in temp_d:
                left_text['titles'] = [home_dict[d][0]]
            if 'text' in temp_d:
                text = [x.strip() for x in home_dict[d][0].split('\r\n')]
                left_text['text'] = text
        if 'right_text_' in temp_d:
            temp_d = temp_d.replace('right_text_', '')
            
            if 'title' in temp_d:
                right_text['titles'] = [home_dict[d][0]]
            if 'text' in temp_d:
                text = [x.strip() for x in home_dict[d][0].split('\r\n')]
                right_text['text'] = text
        if 'tax_text_' in temp_d:
            temp_d = temp_d.replace('tax_text_', '')
            
            if 'title' in temp_d:
                irs_text['titles'] = [home_dict[d][0]]
            if 'text' in temp_d:
                text = [x.strip() for x in home_dict[d][0].split('\r\n')]
                irs_text['text'] = text

    for im in image_list:
        temp_d = im
        print(temp_d, im)
        if 'golf_event_' in temp_d:
            temp_d = temp_d.replace('golf_event_', '')
            if 'image' in temp_d:
                print(image_list[im].name)
                golf_event['images'] = [image_list[im].name]
        if 'two_pic_frame_' in temp_d:
            temp_d = temp_d.replace('two_pic_frame_', '')
            index = temp_d[-1]
            temp_d = temp_d.replace('_'+index, '')
            if 'image_left' in temp_d:
                two_image_frames[index]['images'][0] = image_list[im].name
            if 'image_right' in temp_d:
                two_image_frames[index]['images'][1] = image_list[im].name
    rows = []      
    
    donations = []
    for i in range(len(donation_data['text'])):
        donations += [{'text':donation_data['text'][str(i)], 'val':donation_data['val'][str(i)]}]

    rows += [{'titles':[], 'text':donations, 'images':[], 'format':'count_vals'}]
    
    golf_event['titles'] += golf_event['full_date']
    golf_event.pop('full_date', None)
    rows += [golf_event]
    print(golf_event)
    for i in two_image_frames.keys():
        rows += [two_image_frames[i]]
    
    rows += [left_text]
    rows += [right_text]
    rows += [irs_text]
    
    with open(url_write_backup + 'home.csv', 'w', newline='') as csvfile:
        fieldnames = ['titles', 'text','images', 'format']

        writer = csv.DictWriter(csvfile, delimiter='|', fieldnames=fieldnames)
        writer.writeheader()
        
        writer.writerows(rows)
    
    for im in image_list:
        temp_url = image_path + '/' + image_list[im].name
        picture = Image.open(image_list[im])  
        picture.save(temp_url)
def get_images_home(date_code, type):
    golf_main_context = {}

    if os.getenv('DJANGO_ENV','') == 'local':
        url_main = os.path.dirname(__file__) + '/../media/golf_data/'
    else:
        url_main = staticfiles_storage.path('golf_data')

    with open(url_main + '/about_us.csv', newline='') as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter='|', quotechar='|')
        for row in spamreader:
            d_row = dict(row)
            # if date_code in d_row['year_key']:
            golf_main_context['f'] = d_row

    image_array_str = golf_main_context[type + '_images']
    images = ast.literal_eval(image_array_str)
    
    for i in range(len(images)):
        img = images[i]
        while img.find('/') >= 0:
            img = img[img.find('/')+1:]
        images[i] = img
    return images
def get_home_data():
    data = {'blocks':[], 'two_pics':[],'left':{}, 'right':{}, 'irs':{}}
    if os.getenv('DJANGO_ENV','') == 'local':
        url_main = os.path.dirname(__file__) + '/../media/static_page_data/'
    else:
        url_main = staticfiles_storage.path('static_page_data')

    two_frame_count = 0
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
            elif 'two_pic_frame' == d_row['format']:
                images = ast.literal_eval(d_row['images'])
                titles = ast.literal_eval(d_row['titles'])
                text = ast.literal_eval(d_row['text'])
                
                data['two_pics'] += [{'key':'two_pic_frame', 'title':titles[0], 'descr':'\n'.join(text), 'golf_image_left':images[0], 'golf_image_right':images[1], 'count':two_frame_count}]
                two_frame_count += 1
            elif 'golf_outing' == d_row['format']:
                images = ast.literal_eval(d_row['images'])
                titles = ast.literal_eval(d_row['titles'])
                text = ast.literal_eval(d_row['text'])
                
                data['blocks'] += [{'key':'golf_outing', 'title':titles[0], 'descr':'\n'.join(text), 'date':titles[1], 'file_name':images[0]}]
            elif 'left_panel' == d_row['format'] or 'right_panel' == d_row['format'] or 'irs_panel' == d_row['format']:
                format = d_row['format'].replace('_panel','')
                images = ast.literal_eval(d_row['images'])
                titles = ast.literal_eval(d_row['titles'])
                text = ast.literal_eval(d_row['text'])
                
                data[format] = {'title':titles[0], 'text':'\n'.join(text).strip()}

    return data

# Admin Golf Selection Screen
def golf_view(request):

    context = {'golf_outing':get_event_data()}

    return render(request, 'custAdmin/golf.html', context)

# About Us
def edit_about(request):
    if request.method == 'POST':
        
        form_results = dict(request.POST)
        form_results.pop('csrfmiddlewaretoken')

        git_clone()

        process_about_data(form_results)

        git_publish_all()

    context = {'data':get_about_us_data()}
    
    return render(request, 'custAdmin/about_us_form.html', context)
def get_about_us_data():
    data = []
    if os.getenv('DJANGO_ENV','') == 'local':
        url_main = os.path.dirname(__file__) + '/../media/static_page_data/'
    else:
        url_main = staticfiles_storage.path('static_page_data')

    index = 0
    with open(url_main + '/about_us.csv', newline='') as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter='|', quotechar='|')
        for row in spamreader:
            d_row = dict(row)
            d_row.update({'index':index})
            d_row['text'] = '\n'.join(ast.literal_eval(d_row['text'])).strip()
            data += [d_row]
            index += 1

    return data
def process_about_data(data):

    if os.getenv('DJANGO_ENV','') == 'local':
        url_write_backup = os.path.dirname(__file__) + '/../media/static_page_data/'
    else:
        url_write_backup = os.path.dirname(__file__) + '/git_publishing/deploy/media/static_page_data/'

    write_data = {}
    for d in data.keys():
        index = str(d[-1])
        if index not in write_data.keys():
            write_data.update({index:{'title':'', 'text':[]}})
        
        if d[:d.find('_')] == 'title':
            write_data[index]['title'] = data[d][0]
        if d[:d.find('_')] == 'text':
            write_data[index]['text'] = data[d][0].strip().split('\r\n')

    rows = [x[1] for x in write_data.items()]
    
    with open(url_write_backup + 'about_us.csv', 'w', newline='') as csvfile:
        fieldnames = ['title', 'text']

        writer = csv.DictWriter(csvfile, delimiter='|', fieldnames=fieldnames)
        writer.writeheader()
        
        writer.writerows(rows)

# People 
def edit_people(request):
    if request.method == 'POST':
        
        form_results = dict(request.POST)
        form_results.pop('csrfmiddlewaretoken')

        git_clone()

        process_people_data(form_results)

        redirect('/admin/')
        git_publish_all()

        return home(request)
        
    context = {'data':get_people_data()}

    return render(request, 'custAdmin/people_form.html', context)
def get_people_data():
    data = []
    if os.getenv('DJANGO_ENV','') == 'local':
        url_main = os.path.dirname(__file__) + '/../media/static_page_data/'
    else:
        url_main = staticfiles_storage.path('static_page_data')

    index = 0
    with open(url_main + '/people.csv', newline='') as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter='|', quotechar='|')
        for row in spamreader:
            d_row = dict(row)
            d_row.update({'index':index})
            data += [d_row]
            index += 1
    return data
def process_people_data(data):
    
    if os.getenv('DJANGO_ENV','') == 'local':
        url_write_backup = os.path.dirname(__file__) + '/../media/static_page_data/'
    else:
        url_write_backup = os.path.dirname(__file__) + '/git_publishing/deploy/media/static_page_data/'

    write_data = {}
    for d in data.keys():
        index = str(d[-1])
        if index not in write_data.keys():
            write_data.update({index:{'title':'', 'name':'', 'email':'', 'phone':''}})
        
        if d[:d.find('_')] == 'name':
            write_data[index]['name'] = data[d][0]
        if d[:d.find('_')] == 'title':
            write_data[index]['title'] = data[d][0]
        if d[:d.find('_')] == 'email':
            write_data[index]['email'] = data[d][0]
        if d[:d.find('_')] == 'phone':
            write_data[index]['phone'] = data[d][0]

    rows = [x[1] for x in write_data.items()]
    
    with open(url_write_backup + 'people.csv', 'w', newline='') as csvfile:
        fieldnames = ['name', 'title', 'email','phone']

        writer = csv.DictWriter(csvfile, delimiter='|', fieldnames=fieldnames)
        writer.writeheader()
        
        writer.writerows(rows)

# Golf Classic
def new_golf_classic_request(request):

    if request.method == 'POST':
        
        form_results = dict(request.POST)
        form_results.pop('csrfmiddlewaretoken')
    

        f_date = date.fromisoformat(form_results['full_date'][0])
        git_clone()

        proccess_golf_data(form_results)
        process_golf_images(form_results['full_date'][0], request.FILES)

        git_publish_all()

    # form = GolfForm()
    context = {}
    return render(request, 'custAdmin/golf_form.html', context)
def edit_golf_classic_request(request, key):

    if request.method == 'POST':
        
        form_results = dict(request.POST)
        form_results.pop('csrfmiddlewaretoken')

        git_clone()

        # print(form_results)
        proccess_golf_data(form_results)
        process_golf_images(form_results['full_date'][0], request.FILES)

        git_publish_all()


    outing_data = get_data_by_event_date_code(key)
    outing_data['descr'] = '\r\n'.join(outing_data['descr'])
    context = {'data':outing_data}

    return render(request, 'custAdmin/golf_form.html', context)
def delete_golf_classic_request(request, key):
    
    form_results = {'full_date':[key]}

    git_clone()

    proccess_golf_data(form_results, is_delete=True)
    process_golf_images(form_results['full_date'][0], request.FILES)

    git_publish_all()

    return redirect('/admin/golf')


# Get Current registrations 
def get_golf_registrations(request):
        
    get_payed_registrations('2017-05-13')

    response = FileResponse(open('Golf_Registration.xlsx', 'rb'))
    return response
def get_payed_registrations(date_):
    
    workbook = xlsxwriter.Workbook('Golf_Registration.xlsx')
    worksheet = workbook.add_worksheet()

    worksheet.write(0, 0, 'Contact Email')
    worksheet.write(0, 1, 'Contact First Name')
    worksheet.write(0, 2, 'Contact Last Name')
    worksheet.write(0, 3, 'Group Size')

    row = 1
    for r in FoursomeRegistration.objects.all().filter(date_code=date_).filter(is_payed=True):
        print(r.contact_email, r.golf_1_fname, r.golf_1_lname)
        worksheet.write(row, 0, r.contact_email.replace('[\'','').replace('\']',''))
        worksheet.write(row, 1, r.golf_1_fname.replace('[\'','').replace('\']',''))
        worksheet.write(row, 2, r.golf_1_lname.replace('[\'','').replace('\']',''))
        worksheet.write(row, 3, 'Single' if not r.four else 'Foursome')
        row += 1

    workbook.close()

# Donations
def edit_donations(request):
    if request.method == 'POST':
        
        form_results = dict(request.POST)
        form_results.pop('csrfmiddlewaretoken')

        git_clone()

        process_donation_values(form_results)

        git_publish_all()

    context = {'donations':get_donation_values()}
    return render(request, 'custAdmin/donations_form.html', context)
def process_donation_values(results):
    
    if os.getenv('DJANGO_ENV','') == 'local':
        url_write_backup = os.path.dirname(__file__) + '/../media/static_page_data/'
    else:
        url_write_backup = os.path.dirname(__file__) + '/git_publishing/deploy/media/static_page_data/'

    donations = {}
    for key in results:
        if 'display_value' in key:
            k = 'display_value'
            val = key.replace('display_value_','')
        elif 'stripe_variable' in key:
            k = 'stripe_variable'
            val = key.replace('stripe_variable_','')
        
        if val not in donations:
            donations.update({val:{}})
        if k == 'display_value':
            donations[val].update({'srt':int(results[key][0])})

        donations[val].update({k:results[key][0]})
    
    rows = [donations[x] for x in donations]
    rows = sorted(rows, key = lambda i: i['srt'])
    rows = [{k: v for k, v in x.items() if k != 'srt'} for x in rows]
    
    with open(url_write_backup + 'donations.csv', 'w', newline='') as csvfile:
        fieldnames = ['display_value','stripe_variable']

        writer = csv.DictWriter(csvfile, delimiter='|', fieldnames=fieldnames)
        writer.writeheader()
        
        writer.writerows(rows)
def get_donation_values():
    if os.getenv('DJANGO_ENV','') == 'local':
        url_main = os.path.dirname(__file__) + '/../media/static_page_data/'
    else:
        url_main = staticfiles_storage.path('static_page_data')
    
    context = []
    with open(url_main + '/donations.csv', newline='') as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter='|', quotechar='|')
        i = 0
        for row in spamreader:
            row.update({'count':i})
            context += [row]
            i += 1

    return context

def get_event_data():
    golf_main_context = []
    url_main = staticfiles_storage.path('golf_data/golf.csv')

    with open(url_main, newline='') as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter='|', quotechar='|')
        for row in spamreader:
            d_row = dict(row)
            golf_main_context += [d_row]

    print(golf_main_context)
    return golf_main_context
    
def get_data_by_event_date_code(date_code):
    
    def key_func(k):
        return k['event_day']

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
                d_row.update({'display_count':int(d_row['count'])})
                golf_reg_context += [d_row]

    with open(url_main + '/sponsor_registration.csv', newline='') as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter='|', quotechar='|')
        for row in spamreader:
            d_row = dict(row)
            if date_code in d_row['year_key']:
                d_row.update({'display_count':int(d_row['count'])})
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

    return {
        'course':golf_main_context['golf_course'],
        'active': 'True' == golf_main_context['active'].strip(),
        'open_signup': 'True' == golf_main_context['open_signup'].strip(),
        'date':golf_main_context['year_key'],
        'descr': golf_main_context['description'].split('%&'),
        'schedule':schedule,
        'golf_registration':golf_reg_context,
        'sponsor_registration':sponsor_reg_context,
        'event_images':[{'count':x, 'image_name':img} for x, img in enumerate(get_images(date_code, 'event'))],
        'sponsor_images':[{'count':x, 'image_name':img} for x, img in enumerate(get_images(date_code, 'sponsor'))]
        }
def proccess_golf_data(golf_dict, is_delete = False):

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

    golf_registrations = []
    with open(url_write_backup + 'golf_registration.csv', newline='') as csvfile:
        golf_reader = csv.DictReader(csvfile, delimiter='|', quotechar='|')
        for row in golf_reader:
            d_row = dict(row)
            golf_registrations += [d_row]

    sponsor_registrations = []
    with open(url_write_backup + 'sponsor_registration.csv', newline='') as csvfile:
        golf_reader = csv.DictReader(csvfile, delimiter='|', quotechar='|')
        for row in golf_reader:
            d_row = dict(row)
            sponsor_registrations += [d_row]

    event_schedule = []
    with open(url_write_backup + 'event_schedule.csv', newline='') as csvfile:
        golf_reader = csv.DictReader(csvfile, delimiter='|', quotechar='|')
        for row in golf_reader:
            d_row = dict(row)
            event_schedule += [d_row]

    print(content)
    content = {x['year_key']:x for x in content if x['year_key'] != year_key}
    golf_registrations = {x['year_key'] + x['golf_option_title']:x for x in golf_registrations if x['year_key'] != year_key}
    sponsor_registrations = {x['year_key'] + x['sponsor_option_title']:x for x in sponsor_registrations if x['year_key'] != year_key}
    event_schedule = {x['year_key'] + x['event_day'] + x['time']+ x['description']:x for x in event_schedule if x['year_key'] != year_key}
    
    if not is_delete:
        content.update({year_key:{
            'active': True if 'active' in golf_dict else False,
            'open_signup':True if 'open_signup' in golf_dict else False,
            'year_key':year_key,
            'golf_course':golf_dict['golf_course'][0].strip(),
            'description':golf_dict['description'][0].replace('\r\n','%&').strip(),
            'event_images':get_image_list(year_key, golf_dict, 'event'),
            'sponsor_images':get_image_list(year_key, golf_dict, 'sponsor')
            }})

        golf_option_title = list(filter(lambda x: ('golf_option_title_' in x), golf_dict.keys()))
        stripe_price_input_golf = list(filter(lambda x: ('stripe_price_input_golf_' in x), golf_dict.keys()))
        stripe_price_variable_price_input_golf = list(filter(lambda x: ('stripe_price_variable_price_input_golf_' in x), golf_dict.keys()))
        golf_option_textarea = list(filter(lambda x: ('golf_option_textarea_' in x), golf_dict.keys()))

        [golf_registrations.update({year_key + golf_dict[golf_option_title[x]][0].strip():
            {
                'year_key':year_key,
                'golf_option_title':golf_dict[golf_option_title[x]][0].strip(),
                'price_display':golf_dict[stripe_price_input_golf[x]][0].strip(),
                'stripe_price_variable':golf_dict[stripe_price_variable_price_input_golf[x]][0].strip(),
                'golf_option_textarea':golf_dict[golf_option_textarea[x]][0].strip(),
                'count':x
            }
        }) for x in range(len(golf_option_textarea))]

        sponsor_option_title = list(filter(lambda x: ('sponsor_option_title_' in x), golf_dict.keys()))
        stripe_price_variable_input_sponsor = list(filter(lambda x: ('stripe_price_variable_input_sponsor_' in x), golf_dict.keys()))
        sponsor_option_textarea = list(filter(lambda x: ('sponsor_option_textarea_' in x), golf_dict.keys()))

        [sponsor_registrations.update({year_key + golf_dict[sponsor_option_title[x]][0].strip():
            {
                'year_key':year_key,
                'sponsor_option_title':golf_dict[sponsor_option_title[x]][0].strip(),
                'stripe_price_variable':golf_dict[stripe_price_variable_input_sponsor[x]][0].strip(),
                'sponsor_option_textarea':golf_dict[sponsor_option_textarea[x]][0].strip(),
                'count':x
            }
        }) for x in range(len(sponsor_option_title))]

        new_events = process_schedule(golf_dict,year_key)
        [event_schedule.update({x['year_key'] + x['event_day'] + x['time']+ x['description']:x}) for x in new_events]


    for link in [url_write_backup]:
        with open(link + 'golf.csv', 'w', newline='') as csvfile:
            fieldnames = ['year_key', 'active','open_signup','golf_course', 'description', 'event_images','sponsor_images']

            writer = csv.DictWriter(csvfile, delimiter='|', fieldnames=fieldnames)
            writer.writeheader()
            
            writer.writerows(sorted([content[x] for x in content.keys()], key = lambda i: i['year_key'],reverse=True))
        
        with open(link + 'golf_registration.csv', 'w', newline='') as csvfile:
            fieldnames = ['year_key','golf_option_title', 'price_display', 'stripe_price_variable', 'golf_option_textarea','count']
            
            writer = csv.DictWriter(csvfile, delimiter='|', fieldnames=fieldnames)
            writer.writeheader()
            
            writer.writerows([golf_registrations[x] for x in golf_registrations.keys()])

        with open(link + 'sponsor_registration.csv', 'w', newline='') as csvfile:
            fieldnames = ['year_key', 'sponsor_option_title', 'stripe_price_variable', 'sponsor_option_textarea','count']

            writer = csv.DictWriter(csvfile, delimiter='|', fieldnames=fieldnames)
            writer.writeheader()
            
            writer.writerows([sponsor_registrations[x] for x in sponsor_registrations.keys()])

        with open(link + 'event_schedule.csv', 'w', newline='') as csvfile:
            fieldnames = ['year_key', 'event_day','location', 'time', 'description']

            writer = csv.DictWriter(csvfile, delimiter='|', fieldnames=fieldnames)
            writer.writeheader()
            
            writer.writerows([event_schedule[x] for x in event_schedule.keys()])


            
def process_schedule(golf_dict, year_key):
    keys = list(filter(lambda x: ('day_' in x), golf_dict.keys()))
    schedule = {}
    days = {}
    locations = {}
    
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

    if os.getenv('DJANGO_ENV','') == 'local':
        url_write_backup = os.path.dirname(__file__) + '/../media/images/golf/' + str(f_date.year) + '/'
    else:
        url_write_backup = os.path.dirname(__file__) + '/git_publishing/deploy/media/images/golf/' + str(f_date.year) + '/'

    for link in [url_write_backup]:
        
        for im in image_list:
            print('-', im)
            if 'event' in im or 'sponsor' in im:
                temp_url = link + '/' + image_list[im].name

                print('*', temp_url)
                picture = Image.open(image_list[im])  
                picture.save(temp_url)

    # TODO - save to csv -> date_key|category (event or sponsor)|file_location  
def get_images(date_code, type):
    golf_main_context = {}

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

    image_array_str = golf_main_context[type + '_images']
    images = ast.literal_eval(image_array_str)
    
    for i in range(len(images)):
        img = images[i]
        while img.find('/') >= 0:
            img = img[img.find('/')+1:]
        images[i] = img
    return images
def get_image_list(date_code, golf_dict, type):
    images = list(filter(lambda x: (type + '_image_text_' in x), golf_dict.keys()))
    for i in range(len(images)):
        images[i] = golf_dict[images[i]][0]
        
    actual_images = get_images(date_code, type)
    
    new_images = []
    
    for i in range(max(len(images), len(actual_images))):
        if i >= len(images):
            new_images += [actual_images[i]]
        elif i >= len(actual_images):
            new_images += [images[i]]
        elif images[i] != 'deleted':
            if len(images[i]) > 0:
                new_images += [images[i]]
            else:
                new_images += [actual_images[i]]

    return new_images
     