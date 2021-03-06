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

from s3cwebsite.settings import DOMAIN
from .models import FoursomeRegistration
from django.views.decorators.http import require_POST
from django.conf import settings
import json

stripe.api_key = "sk_test_51JO5STDym2z9hVAOjSsmhioXViLv500Ri8Etu1kcc6roeY9OeA0Ot8B8zZ0obPaMAExSv30itNNd8YaTrA3Rdc5L00poUDRc9W"

from itertools import groupby


# Create your views here.
def home(request):
    context = {}
    context.update(get_home_data())
    # print(context)
    return render(request, 'src/home.html',context)

def our_team(request):

    context = {'people':get_people_data(), 'about':get_about_us_data(), 'address':get_address(), 'social':get_social()}
    return render(request, 'src/our_team.html', context)

def get_golf_outing(request):

    context = {}
    
    context.update(get_data_by_event_date_code(get_active_outing()))
    context.update({'active': is_open_signup(context['date_code'])})
    context.update(get_sign_up_data_event_date_code(context['date_code']))

    
    return render(request, 'src/golf_classic.html',context)

def get_golf_outing_sponsorship(request):

    context = {}
    
    context.update(get_data_by_event_date_code(get_active_outing()))
    context.update({'active': is_open_signup(context['date_code'])})
    context.update(get_sign_up_data_event_date_code(context['date_code']))
    print(context)
    sponsor_ims = chunk_data(context['sponsor_images'], 3)
    while len(sponsor_ims) < 2:
        sponsor_ims += [[]]
    while len(sponsor_ims) != 2:
        sponsor_ims[1] += sponsor_ims[-1]
        sponsor_ims = sponsor_ims[:-1]
        
    context.update({'top_pics':sponsor_ims[0], 'row_of_pics':chunk_data(sponsor_ims[1],4)})
    
    return render(request, 'src/golf_classic_sponsorship.html',context)

def get_golf_outing_by_year(request, year):

    context = {}
    
    get_active_outing()
    context.update(get_data_by_event_date_code(year))
    
    return render(request, 'src/golf_classic.html',context)

def get_golf_outing_involvment(request):
    print('get_golf_outing_involvment')
    year = get_active_outing()

    print(year)
    donation_data = get_donation_data()
    
    context = {'date_code':year, 'active': is_open_signup(year)}
    context.update({'donations':[donation_data[:3],donation_data[3:]]})
    context.update({'home':get_home_data()})
    if is_open_signup(year):
        context.update(get_sign_up_data_event_date_code(year))
        context.update({'contact_email':get_contact_email()})
    
    return render(request, 'src/golf_classic_involvement.html',context)

def get_faq(request):
    if os.getenv('DJANGO_ENV','') == 'local':
        url_main = os.path.dirname(__file__) + '/../media/static_page_data/'
    else:
        url_main = staticfiles_storage.path('static_page_data')
    
    data = []
    with open(url_main + '/faq.csv', newline='') as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter='|', quotechar='|')
        i = 0
        for r in spamreader:
            row = dict(r)
            for k in row:
                row[k] = present_string_arr(ast.literal_eval(row[k]))
            row.update({'index':i})
            print(row)
            data += [row]
            i += 1

    
    return render(request, 'src/faq.html',{'data':data})


def get_golf_outing_involvment_by_year(request, year):
    
    context = {'date_code':year, 'active': is_open_signup(year)}
    context.update(get_sign_up_data_event_date_code(year))
    donation_data = get_donation_data()
    context.update({'donations':[donation_data[:3],donation_data[3:]]})
    context.update({'contact_email':get_contact_email()})
    context.update({'home':get_home_data()})
    
    return render(request, 'src/golf_classic_involvement.html',context)

def get_donation(request):
    
    year = get_active_outing()
    
    context = {'date_code':year}
    context.update({'donations':chunk_data(get_donation_data(), 3)})
    context.update({'home':get_home_data()})
    
    return render(request, 'src/donations.html', context)

class CreateSessionCheckoutView(View):
    def post(self, request, *args, **kwargs):

        registration_type = request.GET.get('type', 'None')
        
        success = settings.DOMAIN.strip() + '/golf-classic-2017-05-13'
        cancel = settings.DOMAIN.strip() 
        
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=[
              'card',
            ],
            line_items=[
                {
                    'price': registration_type,
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=success,
            cancel_url=cancel,
        )
        
        # write update to table for registration, use intent as id
        
        form_results = dict(request.POST)
        form_results.pop('csrfmiddlewaretoken')

        # Checks wether or not registration is for golf (either single or foursome)
        if registration_type == '1s' or registration_type == '4s':
            print(request.GET)
            temp = FoursomeRegistration()
            temp.date_code = request.GET.get('date_code', 'None')
            temp.payment_id = checkout_session.payment_intent
            temp.contact_email = form_results['email']
            temp.golf_1_fname = form_results['fname_1']
            temp.golf_1_lname = form_results['lname_1']
            temp.is_payed = False
            temp.four = False

            if registration_type == '4s':
                temp.golf_2_fname = form_results['fname_2']
                temp.golf_2_lname = form_results['lname_2']
                temp.golf_3_fname = form_results['fname_3']
                temp.golf_3_lname = form_results['lname_3']
                temp.golf_4_fname = form_results['fname_4']
                temp.golf_4_lname = form_results['lname_4']
                temp.four = True

            print(temp)
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

    if (data['type'] == "checkout.session.completed"):
        # For now, you only need to print out the webhook payload so you can see
        # the structure.
        
        # update table to , use intent as id
        registration = FoursomeRegistration.objects.get(payment_id=data['data']['object']['payment_intent'])
        registration.is_payed = True
        registration.save()
        print('Intent hook: ' + data['data']['object']['payment_intent'])

    return HttpResponse(status=200)

@require_POST
@csrf_exempt
def stripe_webhook_paid_endpoint(request):

    payload = request.body.decode('utf-8')
    event = None

    try:
        event = json.loads(payload)
    except:
        print('??????  Webhook error while parsing basic request.' + str(e))
        return HttpResponse(status=200)

    # Handle the event
    if event and event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']  # contains a stripe.PaymentIntent
        print('Payment for {} succeeded'.format(payment_intent['amount']))
        # Then define and call a method to handle the successful payment intent.
        # handle_payment_intent_succeeded(payment_intent)
    elif event['type'] == 'payment_method.attached':
        payment_method = event['data']['object']  # contains a stripe.PaymentMethod
        # Then define and call a method to handle the successful attachment of a PaymentMethod.
        # handle_payment_method_attached(payment_method)
    else:
        # Unexpected event type
        print('Unhandled event type {}'.format(event['type']))

    # return HttpResponse(status=200)

  # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        checkout_session = event['data']['object']
        # Make sure is already paid and not delayed
        if checkout_session['payment_status'] == "paid":
            _handle_successful_payment(checkout_session)

    # Passed signature verification
    return HttpResponse(status=200)

def _handle_successful_payment(checkout_session):
    # Define what to do after the user has successfully paid
    registration = FoursomeRegistration.objects.get(payment_id=checkout_session['payment_intent'])
    registration.is_payed = True
    registration.save()

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

    
    date_obj = date.fromisoformat(date_code)

    # print()
    return {
        'date_code':date_code,
        'year': date_obj.year,
        'course':golf_main_context['golf_course'],
        'date_str': get_week_day(date_obj.weekday()) + ', ' + get_month(date_obj.month) + ' ' + p.ordinal(date_obj.day) + ', ' + str(date_obj.year),
        'descr': golf_main_context['description'].split('%&'),
        'sponsor_description': golf_main_context['sponsor_description'].split('%&'),
        'schedule':schedule,
        'is_golf_registration':True,
        'sponsor_images':ast.literal_eval(golf_main_context['sponsor_images']),
        'event_images':[{'link':'/static/images/golf/' + x, 'visible': 'active' if i == 0 else ''}for i,x in enumerate(ast.literal_eval(golf_main_context['event_images']))],
        'sponsor_images':[{'link':'/static/images/golf/' + x, 'visible': 'active' if i == 0 else ''}for i,x in enumerate(ast.literal_eval(golf_main_context['sponsor_images']))]
        }

def get_sign_up_data_event_date_code(date_code):
    
    golf_sign_ups = []
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
                d_row.update({'description':present_string_arr(ast.literal_eval(d_row['sponsor_option_textarea']))})
                d_row.pop('sponsor_option_textarea')
                sponsor_sign_ups += [d_row]

    count = 0
    with open(url_main + '/golf_registration.csv', newline='') as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter='|', quotechar='|')
        for row in spamreader:
            d_row = dict(row)
            if date_code in d_row['year_key']:
                d_row.update({'description':present_string_arr(ast.literal_eval(d_row['golf_option_textarea']))})
                d_row.pop('golf_option_textarea')
                golf_sign_ups += [d_row]
                count += 1
                
    return {'sponsor_options':sponsor_sign_ups, 'golf_options':golf_sign_ups}
def get_donation_data():
    if os.getenv('DJANGO_ENV','') == 'local':
        url_main = os.path.dirname(__file__) + '/../media/static_page_data/'
    else:
        url_main = staticfiles_storage.path('static_page_data')

    data = []
    with open(url_main + '/donations.csv', newline='') as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter='|', quotechar='|')
        for row in spamreader:
            d_row = dict(row)
            data += [d_row]

    return data

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
                images = present_string_arr(ast.literal_eval(d_row['images']))
                titles = present_string_arr(ast.literal_eval(d_row['titles']))
                text = present_string_arr(ast.literal_eval(d_row['text']))
                
                data['blocks'] += [{'key':'two_pic_frame','img1':images[0], 'img2':images[1], 'title':titles[0], 'text':text}]
            elif 'golf_outing' == d_row['format']:
                images = present_string_arr(ast.literal_eval(d_row['images']))
                titles = present_string_arr(ast.literal_eval(d_row['titles']))
                text = present_string_arr(ast.literal_eval(d_row['text']))
                
                t = 'Join us at S3C\'s ' + titles[0] + ' Annual fundraiseing golf outing'

                data['blocks'] += [{'key':'golf_outing','img1':images[0], 'title':t, 'text':text}]
            elif 'left_panel' == d_row['format'] or 'right_panel' == d_row['format'] or 'irs_panel' == d_row['format']:
                format = d_row['format'].replace('_panel','')
                images = present_string_arr(ast.literal_eval(d_row['images']))
                titles = present_string_arr(ast.literal_eval(d_row['titles']))
                text = present_string_arr(ast.literal_eval(d_row['text']))
                
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

def get_contact_email():
    data = []
    if os.getenv('DJANGO_ENV','') == 'local':
        url_main = os.path.dirname(__file__) + '/../media/static_page_data/'
    else:
        url_main = staticfiles_storage.path('static_page_data')

    with open(url_main + '/organization_information.csv', newline='') as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter='|', quotechar='|')
        for row in spamreader:
            d_row = dict(row)
            data += [d_row]

    return data[0]['contact_email']

def get_address():
    data = []
    if os.getenv('DJANGO_ENV','') == 'local':
        url_main = os.path.dirname(__file__) + '/../media/static_page_data/'
    else:
        url_main = staticfiles_storage.path('static_page_data')

    with open(url_main + '/organization_information.csv', newline='') as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter='|', quotechar='|')
        for row in spamreader:
            d_row = dict(row)
            data += [d_row]

    return [data[0]['street_addr'],data[0]['street_addr_2']] 

def get_social():
    data = []
    if os.getenv('DJANGO_ENV','') == 'local':
        url_main = os.path.dirname(__file__) + '/../media/static_page_data/'
    else:
        url_main = staticfiles_storage.path('static_page_data')

    with open(url_main + '/organization_information.csv', newline='') as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter='|', quotechar='|')
        for row in spamreader:
            d_row = dict(row)
            data += [d_row]

    return data[0]['facebook']

def get_active_outing():
    data = []
    if os.getenv('DJANGO_ENV','') == 'local':
        url_main = os.path.dirname(__file__) + '/../media/golf_data/'
    else:
        url_main = staticfiles_storage.path('golf_data')

    with open(url_main + '/golf.csv', newline='') as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter='|', quotechar='|')
        for row in spamreader:
            d_row = dict(row)
            data += [d_row]

    print(data)
    data = [x['year_key'] for x in list(filter(lambda x: x['active'] == 'True', data))]
    data.sort()
    
    return None if len(data) == 0 else data[-1]

def is_open_signup(year):
    data = []
    if os.getenv('DJANGO_ENV','') == 'local':
        url_main = os.path.dirname(__file__) + '/../media/golf_data/'
    else:
        url_main = staticfiles_storage.path('golf_data')

    with open(url_main + '/golf.csv', newline='') as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter='|', quotechar='|')
        for row in spamreader:
            d_row = dict(row)
            data += [d_row]

    data = [x['open_signup'] for x in list(filter(lambda x: year == x['year_key'], data))]
    
    return data[0] == 'True'

def present_string_arr(s):
    return [x.replace('#apos#','\'') for x in s]

def chunk_data(arr, k):
    n_arr = []
    x = 0
    while x < len(arr):
        if x + k < len(arr):
            n_arr += [arr[x:x+k]]
        else:
            n_arr += [arr[x:]]
        x += k
    return n_arr 