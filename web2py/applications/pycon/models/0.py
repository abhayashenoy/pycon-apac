response.title='Pycon Asia Pacific'
response.subtitle=SPAN('Singapore, 7 - 9 Jun 2012')
from gluon.storage import Storage
from datetime import datetime
import os, sys

settings=Storage()
settings.production=True
settings.home_url='http://127.0.0.1:8000/%s/default' % request.application
settings.start_date=datetime(2012,6,9,00,00)
settings.end_date=datetime(2012,6,11,23,59)
settings.email_server='smtp.webfaction.com'
settings.email_sender='PyCon Apac 2012 <pycon@pugs.org.sg>'
settings.email_login='<email>:<password>'
settings.mailing_list=None
settings.live_site = False
if sys.platform == 'darwin':
    settings.dal_string='sqlite://storage.sqlite'
else:
    settings.live_site = True
    settings.dal_string='postgres://pycon2012:pycon2012@localhost/pycon2012'
try:
    settings.rpx_apikey=open('/Users/mdipierro/janrain_api_key.txt','r').read().strip()
    settings.rpx_domain='web2py'
except: pass

settings.authorize_net=('cnpdev4289', 'SR2P8g4jdEn7vFLQ', True) # sandbox
settings.googlemap_key={
    'localhost': '<secret>', # 127.0.0.1
    'apac.pycon.org': '<secret>',
    'ec2-122-248-193-139.ap-southeast-1.compute.amazonaws.com': '<secret>'
}
settings.calendar_url="http://www.google.com/calendar/embed?src=<calendar>"

settings.sections=('2012','2011','2010','2009','2008','2007')
settings.bibtex="""@InProceedings{hevw%(id)s,
     author    = {%(authors)s}
     title     = {%(title)s}
s     booktitle = {6th High End Visualization Workshop}
     year      = {%(section)s},
     publisher = {Unkown},
     url       = {http://example.com/%(file)s}}
"""

settings.rates = [
    ('001','Corporate ($250)', datetime(2012,1,1),  datetime(2012,5,15,23,59),  250),
    ('002','Regular   ($200)', datetime(2012,1,1),  datetime(2012,5,15,23,59),  200),
    ('003','Corporate ($300)', datetime(2012,5,16), datetime(2012,12,31), 300),
    ('004','Regular   ($250)', datetime(2012,5,16), datetime(2012,12,31), 250),
    ('005','I only want to attend the tutorials', datetime(2012,1,1),  datetime(2012,5,15,23,59), 0),
    ('006','I only want to attend the tutorials', datetime(2012,5,16), datetime(2012,12,31), 0),
    ]

### ('name','key') tutorials with same key overlap in time
settings.tutorials = [
    ('001','Tutorial 1'),
    ('002','Tutorial 2'),
    ('003','Tutorial 3'),
    ('004','Tutorial 4'),
    ('005','Tutorial 5'),
    ('006','Tutorial 6'),
]

settings.tutorial_rate = 75

settings.pricing_policy=lambda rate, tutorials: settings.tutorial_rate*len(tutorials) + [x[4] for x in settings.rates if x[0]==rate][0]

settings.footer="""
powered by [[web2py http://web2py.com]], [[conf2py http://code.google.com/p/conf2py]] ``&copy;``:template 2012 [[pugs http://www.pugs.org.sg]]
"""

settings.difficulty = (
    ('001', 'Beginner'),
    ('002', 'Intermediate'),
    ('003', 'Advanced'),
    ('004', 'Beginner to Intermediate'),
    ('005', 'Intermediate to Advanced'),   
)

settings.permissions = (
    ('001', 'Yes'),
    ('002', 'No'),
)

settings.food_prefs = ('None','Vegetarian','Halal')

settings.tshirt_sizes = ('S','M','L', 'XL')

settings.coupon_email_greeting_user = "Dear %(first_name)s %(last_name)s,"
settings.coupon_email_greeting_generic = "Hello,"
settings.coupon_email_code = """

A coupon has been generated for you by the PyCon Apac Team.

The coupon code is %(code)s. 

This single use coupon entitles you to a discount of S$%(amount)s.

Please use this coupon during registration to avail the discount. You can also update it in your profile before checkout."""

settings.coupon_email_codes = """

%(num)s coupons have been generated for you by the PyCon Apac Team.

The coupon codes are

%(code)s

Each single use coupon entitles you to a discount of S$%(amount)s.

Please use these coupons during registration to avail the discount."""

settings.coupon_email_footer = """

If the amount shown in checkout is incorrect, please contact us at conference@pugs.org.sg.

Regards,
The PyCon Apac 2012 Team"""

settings.coupon_subject = "PyCon Apac 2012 Coupon"

settings.cheque_email = """Dear %(first_name)s %(last_name)s,

Please make out a cheque for S$%(payment_amount)s payable to "Python User Group (Singapore)".
Write our account number - XXXXXXXXX - on the back, and deposit it at any Standard Chartered bank branch.

Here is a list of Standard Chartered bank branches
http://www.standardchartered.com.sg/branch-directory/en/

Thank you,
The PyCon Apac 2012 Team"""

settings.cheque_subject = "Cheque payment for PyCon Apac 2012"

settings.cert_id = '<paypal-certid>'
settings.public_cert = os.path.join(request.folder, 'private', 'abhaya-pubcert.pem')
settings.private_cert = os.path.join(request.folder, 'private', 'abhaya-prvkey.pem')
settings.paypal_cert = os.path.join(request.folder, 'private', 'paypal_cert_pem.txt')

settings.paypal_url = 'https://www.paypal.com/cgi-bin/webscr'
settings.paypal_business_email = 'paypal@pugs.org.sg'

settings.invalid_ipn_email = 'tracker = %s, query = %s, db id = %s'

settings.administrator = 'abhayashenoy@gmail.com'
