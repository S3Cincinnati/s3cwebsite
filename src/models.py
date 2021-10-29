from django.db import models

# Create your models here.
class FoursomeRegistration(models.Model):
    date_code = models.CharField(max_length=12)
    payment_id = models.CharField(max_length=100) 
    contact_email = models.CharField(max_length=100)
    golf_1_fname = models.CharField(max_length=50)
    golf_1_lname = models.CharField(max_length=50)
    golf_2_fname = models.CharField(max_length=50)
    golf_2_lname = models.CharField(max_length=50)
    golf_3_fname = models.CharField(max_length=50)
    golf_3_lname = models.CharField(max_length=50)
    golf_4_fname = models.CharField(max_length=50)
    golf_4_lname = models.CharField(max_length=50)
    is_payed = models.BooleanField()
    four = models.BooleanField()

    def __str__(self):
        return 'date_code: ' + self.date_code + '; payment_id: ' + self.payment_id + '; ' + ('payed' if self.is_payed else 'not payed')