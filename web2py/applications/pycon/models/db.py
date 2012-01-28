# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
#########################################################################

if request.env.web2py_runtime_gae:            # if running on Google App Engine
    db = DAL('gae')                           # connect to Google BigTable
    # session.connect(request, response, db=db) # and store sessions and tickets there
    ### or use the following lines to store sessions in Memcache
    # from gluon.contrib.memdb import MEMDB
    # from google.appengine.api.memcache import Client
    # session.connect(request, response, db=MEMDB(Client())
else:                                         # else use a normal relational database
    db = DAL(settings.dal_string)             # if not, use SQLite or other DB
## if no need for session
# session.forget()
session.connect(request, response, db=db) # store sessions and tickets in the db

#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - crud actions
## comment/uncomment as needed

from gluon.tools import *
auth=Auth(globals(),db)              # authentication/authorization
crud=Crud(globals(),db)              # for CRUD helpers using auth
service=Service(globals())           # for json, xml, jsonrpc, xmlrpc, amfrpc

COUNTRIES=['Singapore', 'Afghanistan', 'Albania', 'Algeria', 'Andorra', 'Angola', 'Antigua and Barbuda', 'Argentina', 'Armenia', 'Australia', 'Austria', 'Azerbaijan', 'Bahamas', 'Bahrain', 'Bangladesh', 'Barbados', 'Belarus', 'Belgium', 'Belize', 'Benin', 'Bhutan', 'Bolivia', 'Bosnia and Herzegovina', 'Botswana', 'Brazil', 'Brunei', 'Bulgaria', 'Burkina Faso', 'Burundi', 'Cambodia', 'Cameroon', 'Canada', 'Cape Verde', 'Central African Republic', 'Chad', 'Chile', 'China', 'Colombia', 'Comoros', 'Congo', 'Costa Rica', "C&ocirc;te d'Ivoire", 'Croatia', 'Cuba', 'Cyprus', 'Czech Republic', 'Denmark', 'Djibouti', 'Dominica', 'Dominican Republic', 'East Timor', 'Ecuador', 'Egypt', 'El Salvador', 'Equatorial Guinea', 'Eritrea', 'Estonia', 'Ethiopia', 'Fiji', 'Finland', 'France', 'Gabon', 'Gambia', 'Georgia', 'Germany', 'Ghana', 'Greece', 'Grenada', 'Guatemala', 'Guinea','Guinea-Bissau', 'Guyana', 'Haiti', 'Honduras', 'Hong Kong', 'Hungary', 'Iceland', 'India', 'Indonesia', 'Iran', 'Iraq', 'Ireland', 'Israel', 'Italy', 'Jamaica', 'Japan', 'Jordan', 'Kazakhstan', 'Kenya', 'Kiribati', 'North Korea','South Korea', 'Kuwait', 'Kyrgyzstan', 'Laos', 'Latvia', 'Lebanon', 'Lesotho', 'Liberia', 'Libya', 'Liechtenstein', 'Lithuania', 'Luxembourg', 'Macedonia', 'Madagascar', 'Malawi', 'Malaysia', 'Maldives', 'Mali', 'Malta', 'Marshall Islands', 'Mauritania', 'Mauritius', 'Mexico', 'Micronesia', 'Moldova', 'Monaco', 'Mongolia', 'Montenegro', 'Morocco', 'Mozambique', 'Myanmar', 'Namibia', 'Nauru', 'Nepal', 'Netherlands', 'New Zealand', 'Nicaragua', 'Niger', 'Nigeria', 'Norway', 'Oman', 'Pakistan', 'Palau', 'Palestine', 'Panama', 'Papua New Guinea', 'Paraguay', 'Peru', 'Philippines', 'Poland', 'Portugal', 'Puerto Rico', 'Qatar', 'Romania', 'Russia', 'Rwanda', 'Saint Kitts and Nevis', 'Saint Lucia', 'Saint Vincent and the Grenadines', 'Samoa', 'San Marino', 'Sao Tome and Principe', 'Saudi Arabia', 'Senegal', 'Serbia and Montenegro', 'Seychelles', 'Sierra Leone', 'Slovakia', 'Slovenia', 'Solomon Islands', 'Somalia', 'South Africa', 'Spain', 'Sri Lanka', 'Sudan', 'Suriname', 'Swaziland', 'Sweden', 'Switzerland', 'Syria', 'Taiwan', 'Tajikistan', 'Tanzania', 'Thailand', 'Togo', 'Tonga', 'Trinidad and Tobago', 'Tunisia', 'Turkey', 'Turkmenistan', 'Tuvalu', 'Uganda', 'Ukraine', 'United Arab Emirates', 'United Kingdom', 'United States', 'Uruguay', 'Uzbekistan', 'Vanuatu', 'Vatican City', 'Venezuela', 'Vietnam', 'Yemen', 'Zambia', 'Zimbabwe']


def Hidden(*a,**b):
    b['writable']=b['readable']=False
    return Field(*a,**b)

class IS_VALID_TUTORIAL(IS_IN_SET):
    def __call__(self, value):
        value, err = super(IS_VALID_TUTORIAL, self).__call__(value)
        if err:
            return value, err

        if len(value) > 2 or len(set(map(lambda x: x % 2, map(int, value)))) != len(value):
            return (value, self.error_message)
        return (value, None)

fields=[
    Hidden('manager','boolean',default=False),
    Hidden('editor','boolean',default=False),
    Hidden('registered','boolean',default=False),
    Hidden('first_time','boolean',default=True),
    Hidden('paid','boolean',default=False),
    Hidden('payment_amount','double',default=0.0),
    Hidden('payment_datetime','datetime',default=request.now),
    Hidden('payment_invoice',default=''),
    Field('first_name', length=512,default='',comment='*',
        requires=(IS_NOT_EMPTY(error_message='Enter your name'))),
    Field('last_name', length=512,default='',comment='*'),
    Field('email', length=512,default='',comment='*',
        requires=(IS_EMAIL(error_message='Enter a valid email address'),
            IS_NOT_IN_DB(db,'auth_user.email', error_message='That email address is already in use'))),
    Field('password', 'password', readable=False, label='Password', comment='*',
        requires=[IS_NOT_EMPTY(error_message='Enter a password'),
            CRYPT(auth.settings.hmac_key)]),
    Field('rate','string', label='Registration rate', comment='*',
          requires=IS_IN_SET([x[0:2] for x in settings.rates if x[2]<=request.now<=x[3]],
              error_message='Choose your registration rate')),
    Field('web_page',label='Website',requires=IS_EMPTY_OR(IS_URL())),
    Field('phone',default=''),
    Field('co', label='Company', default=''),
    Field('co_url', label='Company Website', default=''),
    Field('street', label='Street Address', default=''),
    Field('city', default=''),
    Field('country',requires=IS_IN_SET(COUNTRIES,
        error_message='Tell us where you\'re from'),comment='*'),
    Field('dietary_preferences', label='Food preference',
          requires=IS_IN_SET(settings.food_prefs, zero=None)),
    Field('tshirt', label='TShirt Size',
          requires=IS_IN_SET(settings.tshirt_sizes, zero=None)),
    Field('tutorials','list:string', label='Choose up to two tutorials',
          requires=IS_VALID_TUTORIAL(settings.tutorials, multiple=True,
              error_message='Your tutorial selections clash')),
    Field('short_profile','text',default=''),
    Field('profile_picture','upload'),
    Field('make_profile_public','boolean',default=False),
    Field('accompanied_by','integer', label='Is anyone visiting Singapore with you ?',
          requires=IS_IN_SET(range(5),zero=None)),
    Hidden('latitude','double',requires=IS_FLOAT_IN_RANGE(-90,90)),
    Hidden('longitude','double', requires=IS_FLOAT_IN_RANGE(-180,180)),
    Field('discount_coupon','string'),
    Hidden('registered_by','integer',default=0), #nobody
    Hidden('registration_id', length=512,default=''),
    Hidden('registration_key', length=512,default=''),
    Hidden('reset_password_key', length=512,default='',
          label=auth.messages.label_reset_password_key),
    Field('nick','string', label='Name on badge'),
    Field('badge_1','string', label='Badge Line 1'),
    Field('badge_2','string', label='Badge Line 2'),
    Hidden('cheque', 'string', label='Cheque number'),
    Hidden('paypal_tracker', 'string'),
    Hidden('speaker', 'boolean', default=False),
    Hidden('guest', 'boolean', default=False),
    ]

db.define_table('auth_user',
                format='%(first_name)s %(last_name)s',
                *fields
                )

db.auth_user.manager.default = db(db.auth_user.id>0).count()==0
db.auth_user.id.represent=lambda id: A(id,_href=URL('d','manage_users',args=id), _target='_top')

def lola(form):
    form.vars.registered=True
    if settings.mailing_list and form.vars.subscribe_mailing_list:
        sender=mail.settings.sender
        mail.settings.sender=form.vars.email
        mail.send(to=settings.mailing_list,message='subscribe')
        mail.settings.sender=sender
    if form.vars.country:
        form.vars.longitude, form.vars.latitude = geocode("%s %s" % (form.vars.city, form.vars.country))
    if int(form.vars.rate) > 4 and not form.vars.tutorials:
        form.errors.tutorials = 'Pick at least one tutorial'
    if not form.record or (form.record and not form.record.paid):
        amount=settings.pricing_policy(form.vars.rate,form.vars.tutorials)
        if form.vars.discount_coupon:
            coupon = db.coupon(code=form.vars.discount_coupon, used=False)
            if coupon and (coupon.used==False or coupon.used_by==form.vars.id)\
                and (form.vars.rate == '002' or form.vars.rate == '004'):
                amount=max(amount - coupon.amount, 0)
                coupon.update_record(used=True,
                                     used_by=form.vars.id,
                                     used_in=request.now)
            else:
                form.errors.discount_coupon='Invalid coupon code'
                if coupon and (form.vars.rate != '002' or form.vars.rate != '004'):
                    form.errors.discount_coupon = 'Your coupon is not valid for this registration rate'
        form.vars.payment_amount = amount
    if not form.record and not len(form.errors):
        mail.send(to=form.vars.email,
            subject='PyCon Apac 2011 Registration',
            message="""Dear %(first_name)s %(last_name)s,

Thank you for registering for PyCon Apac 2011.

If you wish do a group registration, you can do so at http://%(group_reg_url)s

If you haven't already done so, you can pay for your conference pass at http://%(checkout_url)s

Thank you,
The PyCon Apac 2011 Team
http://apac.pycon.org""" % dict(first_name=form.vars.first_name,
                    last_name=form.vars.last_name,
                    group_reg_url=request.env.http_host + URL(r=request, c='d', f='register_other'),
                    checkout_url=request.env.http_host + URL(r=request, c='d', f='checkout')))


auth.settings.register_onvalidation=lola
auth.settings.profile_onvalidation=lola
auth.settings.formstyle='ul'

crud.settings.create_onvalidation.auth_user.append(lola)
crud.settings.update_onvalidation.auth_user.append(lola)
crud.settings.formstyle='ul'


manager = auth.user and auth.user.manager or auth.user_id==1
editor = auth.user and auth.user.editor or auth.user_id==1

mail=Mail()
mail.settings.server=settings.email_server if settings.production else 'logging'
mail.settings.sender=settings.email_sender
mail.settings.login=settings.email_login

_verified_email = """Dear %(first_name)s %(last_name)s,

Thank you for verifying your email address

You can now pay for your conference pass at http://"""+\
request.env.http_host+URL(r=request, c='d', f='checkout') +\
"""

Thank you,
The PyCon Apac 2011 Team
http://apac.pycon.org
"""

def _send_verified_email(user):
    mail.send(to=user.email,
        subject='PyCon Apac 2011 Registration',
        message=_verified_email % dict(first_name=user.first_name,
            last_name=user.last_name, url=request.env.http_host + URL(r=request, c='d', f='checkout')))

auth.settings.hmac_key='asdj1owiuydqoskmasj2o37y0woidjalsdnamskjdnasi'
auth.define_tables()
auth.settings.mailer=mail
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.messages.verify_email = """
Hello,

Thank you for registering for PyCon Apac 2011

Please visit http://""" +\
request.env.http_host+URL(r=request, c='d', f='user', args=['verify_email']) +\
"""/%(key)s to verify your email address.

You can then pay for your conference pass or register others for the conference

Thank you,
The PyCon Apac 2011 Team
http://apac.pycon.org
"""

auth.settings.reset_password_requires_verification = True
auth.messages.reset_password = 'Click http://'+request.env.http_host+URL(r=request,c='d',f='user',args=['reset_password'])+'/%(key)s to reset your password'
auth.messages.email_sent='An email has been sent to you. Please follow the instructions in it to proceed'
auth.settings.register_next = 'index'
auth.messages.email_verified = 'Thank you. Your email has been verified. You can now login'
auth.messages.registration_verifying = 'Verify your email address to login'
auth.settings.verify_email_onaccept = _send_verified_email

def _setup_group_membership(form):
    email = form.vars.email
    user = db(db.auth_user.email==email).select()
    if not user:
        return
    user = user[0]
    community_group = db(db.auth_group.role == 'community').select()[0]
    db.auth_membership.insert(user_id=user.id, group_id=community_group.id)
    db.commit()

auth.settings.register_onaccept = _setup_group_membership

auth.settings.login_captcha = False
auth.settings.register_captcha = Recaptcha(request,
    '6LfPzMASAAAAAPx0VBi4NkfbUko1r2SbsA1285x7',
    '6LfPzMASAAAAALA1S9vApCUEMcEDCq5QG_HNVYkj',
    label='Are you human ?',
    error_message='Your text didn\'t match. Try again')
#auth.settings.captcha = False

if settings.rpx_domain:
    from gluon.contrib.login_methods.rpx_account import RPXAccount
    auth.settings.actions_disabled=['register','change_password',
                                    'request_reset_password']
    auth.settings.login_form = RPXAccount(request,
                                          api_key=settings.rpx_apikey,
                                          domain=settings.rpx_domain,
                                          url = settings.home_url+"/user/login")
    if request.function=='user' and request.args(0)=='register':
        if not auth.user_id: redirect(URL('user',args='login'))
        else: redirect(URL('user',args='profile'))
    if auth.user and not auth.user.registered:
        if not (request.function=='user' and request.args(0)=='profile'):
            redirect(URL('user',args='profile'))


db.define_table('paypal_txns',
    Field('txn_id', 'string'),
    Field('tracker', 'string'),
    Field('ipn_vars', 'text'),
    Field('time_recvd', 'datetime', default=request.now),
    Field('status', 'boolean'))
