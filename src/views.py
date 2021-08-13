from django.http.response import JsonResponse
from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
import csv
from django.contrib.staticfiles.storage import staticfiles_storage
from datetime import date

from stripe.api_resources import checkout
import inflect
import json
import os
import stripe
from django.shortcuts import redirect

stripe.api_key = "sk_test_51JO5STDym2z9hVAOjSsmhioXViLv500Ri8Etu1kcc6roeY9OeA0Ot8B8zZ0obPaMAExSv30itNNd8YaTrA3Rdc5L00poUDRc9W"


# Create your views here.
def home(request):
    context = {}
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
    context = {'people':people}
    return render(request, 'src/our_team.html', context)


def get_golf_outing(request, year):

    print(year)
    context = {}
    context.update(get_data_by_event_date_code(year))
    
    return render(request, 'src/golf_classic.html',context)

def get_golf_outing_involvment(request, year):

    # if request.method == 'POST':
        

    print(year)
    context = {}
    context.update(get_data_by_event_date_code(year))

    
    
    return render(request, 'src/golf_classic_involvement.html',context)


class createSessionCheckoutView(View):
    def post(self, request, *args, **kwargs):
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=[
              'card',
            ],
            line_items=[
                {
                    # TODO: replace this with the `price` of the product you want to sell
                    'price': 'price_1JO6E6Dym2z9hVAOoheeE5fx',
                    'quantity': 1,
                },
            ],
            mode='payment',
            # success_url=YOUR_DOMAIN + '/success.html',
            # cancel_url=YOUR_DOMAIN + '/cancel.html',
            success_url='http://localhost:8000/golf-classic-2017-05-13',
            cancel_url='http://localhost:8000/',
        )

        # return JsonResponse({
        #     'id':checkout_session.id
        # })
        return redirect(checkout_session.url, code=303)

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

    date_obj = date.fromisoformat(date_code)
    p = inflect.engine()

    return {
        'year': date_obj.year,
        'course':golf_main_context['golf_course'],
        'date_str': get_week_day(date_obj.weekday()) + ', ' + get_month(date_obj.month) + ' ' + p.ordinal(date_obj.day) + ', ' + str(date_obj.year),
        'descr': golf_main_context['description'].split('%&'),
        'schedule':schedule,
        'is_golf_registration':True
        }

def get_week_day(day_val):
    mapp = {0:'Monday', 1:'Tuesday',2:'Wednesday',3:'Thursday',4:'Friday',5:'Saturday',6:'Sunday'}

    return mapp[day_val]

def get_month(month_val):
    mapp = {1:'January',2:'February',3:'March',4:'April',5:'May',6:'June',7:'July',8:'August',9:'September',10:'October',11:'November',12:'December'}

    return mapp[month_val]