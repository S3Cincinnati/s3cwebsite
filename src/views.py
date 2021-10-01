from django.http.response import JsonResponse
from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
import csv
from django.contrib.staticfiles.storage import staticfiles_storage
from datetime import date
import ast

from stripe.api_resources import checkout
import inflect
import json
import os
import stripe
from django.shortcuts import redirect

from django.views.decorators.csrf import csrf_exempt
from .models import FoursomeRegistration

stripe.api_key = "sk_test_51JO5STDym2z9hVAOjSsmhioXViLv500Ri8Etu1kcc6roeY9OeA0Ot8B8zZ0obPaMAExSv30itNNd8YaTrA3Rdc5L00poUDRc9W"

from itertools import groupby


# Create your views here.
def home(request):
    context = {}
    context.update(get_home_data())
    # print(context)
    return render(request, 'src/home.html',context)

def our_team(request):

    people = [
        {
            'name':'Darryn G. Chenault',
            'position':'Event Coordinator – Golf Classic',
            'email':'dchenault@finneytown.org',
            'number':'513-233-1861'
        },
        {
            'name':'Sherrie Chenault',
            'position':'Volunteer Coordinator',
            'email':'sherrie.chenault@fuse.net',
            'number':'513-295-4241'
        },
        {
            'name':'Julian Deese',
            'position':'Event Site Manager',
            'email':'juliandeese@gmail.com',
            'number':'513-225-6068'
        }
    ]
    
    context = {'people':people, 'about':get_about_us_data()}
    return render(request, 'src/our_team.html', context)


def get_golf_outing(request, year):

    context = {}
    context.update(get_data_by_event_date_code(year))
    
    return render(request, 'src/golf_classic.html',context)

def get_golf_outing_involvment(request, year):

    # if request.method == 'POST':
        

    # print(year)
    # print(FoursomeRegistration.objects.all())
    context = {}
    context.update(get_sign_up_data_event_date_code(year))

    print(context)
    
    return render(request, 'src/golf_classic_involvement.html',context)


class CreateSessionCheckoutView(View):
    def post(self, request, *args, **kwargs):
        

        registration_type = request.GET.get('type', 'None')

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=[
              'card',
            ],
            line_items=[
                {
                    'price': get_price(registration_type),
                    'quantity': 1,
                },
            ],
            mode='payment',
            # success_url=YOUR_DOMAIN + '/success.html',
            # cancel_url=YOUR_DOMAIN + '/cancel.html',
            success_url='http://localhost:8000/golf-classic-2017-05-13',
            cancel_url='http://localhost:8000/',
        )
        
        # write update to table for registration, use intent as id
        
        form_results = dict(request.POST)
        form_results.pop('csrfmiddlewaretoken')

        # Checks wether or not registration is for golf (either single or foursome)
        if registration_type == '1s' or registration_type == '4s':
            temp = FoursomeRegistration()
            temp.date_code = request.GET.get('date_code', 'None')
            temp.payment_id = checkout_session.payment_intent
            temp.contact_email = form_results['email']
            temp.golf_1_fname = form_results['fname_1']
            temp.golf_1_lname = form_results['lname_1']
            temp.is_payed = False

            if registration_type == '4s':
                temp.golf_2_fname = form_results['fname_2']
                temp.golf_2_lname = form_results['lname_2']
                temp.golf_3_fname = form_results['fname_3']
                temp.golf_3_lname = form_results['lname_3']
                temp.golf_4_fname = form_results['fname_4']
                temp.golf_4_lname = form_results['lname_4']

            temp.save()

        return redirect(checkout_session.url, code=303)



# stripe.api_key = "sk_test_51JO5STDym2z9hVAOjSsmhioXViLv500Ri8Etu1kcc6roeY9OeA0Ot8B8zZ0obPaMAExSv30itNNd8YaTrA3Rdc5L00poUDRc9W"
def key_func(k):
    return k['event_day']

@csrf_exempt
def my_webhook_view(request):
    payload = request.body
    # valid_json_string = "[" + payload + "]"  # or "[{0}]".format(your_string)
    data = json.loads(payload)

    print(data['type'])
    if (data['type'] == "checkout.session.completed"):
        # For now, you only need to print out the webhook payload so you can see
        # the structure.
        
        # update table to , use intent as id
        registration = FoursomeRegistration.objects.get(payment_id=data['data']['object']['payment_intent'])
        registration.is_payed = True
        registration.save()
        print('Intent hook: ' + data['data']['object']['payment_intent'])

    return HttpResponse(status=200)

def get_data_by_event_date_code(date_code):
    
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
    
    events = []
    with open(url_main + '/event_schedule.csv', newline='') as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter='|', quotechar='|')
        for row in spamreader:
            d_row = dict(row)
            if date_code in d_row['year_key']:
               events += [d_row]

    schedule = []

    p = inflect.engine()

    for key, value in groupby(events, key_func):
        date_obj = date.fromisoformat(key)
        data = list(value)
        schedule += [{
            'date':key,
            'date_str':get_week_day(date_obj.weekday()) + ', ' + get_month(date_obj.month) + ' ' + p.ordinal(date_obj.day) + ', ' + str(date_obj.year), 
            'location':' ' if len(data) == 0 else data[0]['location'],
            'data':data}]

    # schedule = [schedule[x] for x in schedule.keys()]
    print(schedule)
    date_obj = date.fromisoformat(date_code)

    print('**', golf_main_context['sponsor_images'])
    # print()
    return {
        'date_code':date_code,
        'year': date_obj.year,
        'course':golf_main_context['golf_course'],
        'date_str': get_week_day(date_obj.weekday()) + ', ' + get_month(date_obj.month) + ' ' + p.ordinal(date_obj.day) + ', ' + str(date_obj.year),
        'descr': golf_main_context['description'].split('%&'),
        'schedule':schedule,
        'is_golf_registration':True,
        'sponsor_images':ast.literal_eval(golf_main_context['sponsor_images'])
        }

def get_sign_up_data_event_date_code(date_code):
    
    golf_sign_ups = {'1s':{}, '4s':{}}
    sponsor_sign_ups = []

    if os.getenv('DJANGO_ENV','') == 'local':
        url_main = os.path.dirname(__file__) + '/../media/golf_data/'
    else:
        url_main = staticfiles_storage.path('golf_data')

    with open(url_main + '/sponsor_registration.csv', newline='') as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter='|', quotechar='|')
        for row in spamreader:
            d_row = dict(row)
            if date_code in d_row['year_key']:
                d_row.update({'description':d_row['sponsor_option_textarea'].split(';')})
                d_row.pop('sponsor_option_textarea')
                sponsor_sign_ups += [d_row]

    with open(url_main + '/golf_registration.csv', newline='') as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter='|', quotechar='|')
        for row in spamreader:
            d_row = dict(row)
            if date_code in d_row['year_key']:
                d_row.update({'description':d_row['golf_option_textarea'].split(';')})
                d_row.pop('golf_option_textarea')
                if d_row['golf_option_title'] == '1s':
                    golf_sign_ups['1s'] = d_row
                if d_row['golf_option_title'] == '4s':
                    golf_sign_ups['4s'] = d_row
    
    return {'sponsor_options':sponsor_sign_ups, 'golf_options':golf_sign_ups}

def get_home_data():
    data = {'blocks':[], 'two_pics':[]}
    if os.getenv('DJANGO_ENV','') == 'local':
        url_main = os.path.dirname(__file__) + '/../media/static_page_data/'
    else:
        url_main = staticfiles_storage.path('static_page_data')

    with open(url_main + '/home.csv', newline='') as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter='|', quotechar='|')
        for row in spamreader:
            d_row = dict(row)
            if 'count_vals' == d_row['format']:
                data['blocks'] += [{'key':'count_vals','vals':ast.literal_eval(d_row['text'])}]
                # d_row.pop('sponsor_option_textarea')
                # sponsor_sign_ups += [d_row]
            elif 'two_pic_frame' == d_row['format']:
                images = ast.literal_eval(d_row['images'])
                titles = ast.literal_eval(d_row['titles'])
                text = ast.literal_eval(d_row['text'])
                
                data['two_pics'] += [{'key':'two_pic_frame','img1':images[0], 'img2':images[1], 'title':titles[0], 'text':text}]
            elif 'golf_outing' == d_row['format']:
                images = ast.literal_eval(d_row['images'])
                titles = ast.literal_eval(d_row['titles'])
                text = ast.literal_eval(d_row['text'])
                
                t = 'Join us at S3C\'s ' + titles[0] + ' Annual fundraiseing golf outing'

                data['blocks'] += [{'key':'golf_outing','img1':images[0], 'title':t, 'text':text}]
            elif 'left_panel' == d_row['format'] or 'right_panel' == d_row['format'] or 'irs_panel' == d_row['format']:
                format = d_row['format'].replace('_panel','')
                images = ast.literal_eval(d_row['images'])
                titles = ast.literal_eval(d_row['titles'])
                text = ast.literal_eval(d_row['text'])
                
                data[format] = {'title':titles[0], 'text':text}
    
    return data
def get_week_day(day_val):
    mapp = {0:'Monday', 1:'Tuesday',2:'Wednesday',3:'Thursday',4:'Friday',5:'Saturday',6:'Sunday'}

    return mapp[day_val]

def get_month(month_val):
    mapp = {1:'January',2:'February',3:'March',4:'April',5:'May',6:'June',7:'July',8:'August',9:'September',10:'October',11:'November',12:'December'}

    return mapp[month_val]

def get_price(type):
    if type == '1s':
        return 'price_1JO6mKDym2z9hVAODSFPgWcO'
    if type == '4s':
        return 'price_1JO6ffDym2z9hVAOVc18C5tx'
    return ''

def get_about_us_data():
    data = []
    if os.getenv('DJANGO_ENV','') == 'local':
        url_main = os.path.dirname(__file__) + '/../media/static_page_data/'
    else:
        url_main = staticfiles_storage.path('static_page_data')

    with open(url_main + '/about_us.csv', newline='') as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter='|', quotechar='|')
        for row in spamreader:
            d_row = dict(row)
            d_row['text'] = ast.literal_eval(d_row['text'])
            data += [d_row]

    return data
# class C