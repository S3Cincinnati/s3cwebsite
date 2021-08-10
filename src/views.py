from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def home(request):
    context = {}
    return render(request, 'src/home.html',context)

def get_golf_outing(request, year):

    # TODO check year

    # TODO get sample data from csv

    Description = "Join us for the 9th Annual S3C Golf Classic on Saturday, May 13, 2017 at Glenview Golf Course.\nS3C Golf Classic offers an all-inclusive golf experience for all ages and golf skill levels. Golfers will receive 18 holes of golf, lunch, dinner, beer, soft drinks, gifts, and games of chance for a $100 donation to the Cancer Community!  Golf is played in a scramble format.\nS3C will use participants' tax-deductible donations to help families impacted by cancer afford everyday living needs, support local cancer organizations, and partner with Cincinnati Children's to create smiles throughout the Oncology Unit.\n We also welcome you to join us to help us kick-off our weekend!  On Friday, May 12, 2017 we are partnering with Cincinnati Firefighters Local 48 and Cincinnati African-American Fire Fighters to host a charity cookout at Century Inn Restaurant and Tavern from 6:00 – 10:00 pm.  All proceeds benefit the Firefighters Cancer Fund.  No registration is required to participate - $10.00 entry at the door."
    schedule = [
        {
            'date': 'Friday, May 12, 2017',
            'location':'Century Inn Restaurant & Tavern',
            'events':[
                {
                    'time':'6:00 - 10:00 pm',
                    'description':'Beer, Cornhole, Volleyball, Music, Raffles' 
                }
            ]
        },
        {
            'date': 'Saturday, May 13, 2017',
            'location':'Glenview Golf Course',
            'events':[
                {
                    'time':'11:30 am',
                    'description':'Registration and Range Opens' 
                },
                {
                    'time':'12:15 pm',
                    'description':'Food and Beer Served' 
                },
                {
                    'time':'1:30 pm',
                    'description':'Shotgun Start' 
                },
                {
                    'time':'6:30 pm',
                    'description':'Dinner and Awards' 
                }
            ]
        }
    ]
    context = {
        'year':year,
        'course':'Glenview Golf Course',
        'date_str':'Saturday, May 7th, 2016',
        'descr': Description.split('\n'),
        'schedule':schedule
        }
    return render(request, 'src/golf_classic.html',context)