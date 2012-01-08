# -*- coding: utf-8 -*- 

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################  

import itertools
import uuid
from urllib2 import urlopen
from applications.pycon.modules.cart import cart_details

def index():
    if auth.user and auth.user.first_time:
        auth_user = db(db.auth_user.id==auth.user.id).select().first()
        auth_user.update_record(first_time=False)
        redirect(URL('checkout'))
    return dict(page=db.plugin_wiki_page(slug='index'))

def participants():
    orderby=db.auth_user.first_name|db.auth_user.last_name
    query=db.auth_user.id>0
    if not auth.user or not auth.user.manager:
        query=query&(db.auth_user.make_profile_public==True)
    attendees=db(query).select(orderby=orderby)
    return dict(attendees=attendees)

def schedule(): return dict()

def get(table,onerror='manage_talks'):
    url=URL(onerror)
    try:
        id=int(request.args(0))
    except:
        redirect(url)
    record=table[id]
    if not record:
        redirect(url)
    return record

@auth.requires_login()
def register_other():
    db.auth_user.email.writable=db.auth_user.email.readable=True
    db.auth_user.registered_by.default=auth.user.id
    
    db.auth_user.rate.default=auth.user.rate
    db.auth_user.co.default=auth.user.co
    db.auth_user.co_url.default=auth.user.co_url
    db.auth_user.street.default=auth.user.street
    db.auth_user.city.default=auth.user.city
    db.auth_user.country.default=auth.user.country
    
    record=db.auth_user(request.args(0) or 0,registered_by=auth.user.id)
    if record and record.paid:
        db.auth_user.rate.writable=False
        db.auth_user.tutorials.writable=False
    if record:
        crud.messages.submit_button = 'Save'
        form=crud.update(db.auth_user,
                         record,
                         message='User updated')
    else:
        crud.messages.submit_button = 'Register'
        form=crud.create(db.auth_user,
                         message='User created')
    users=db(db.auth_user.registered_by==auth.user.id).select()
    return dict(form=form,users=users)

@auth.requires_login()
def checkout():
    from applications.pycon.modules import paypal
    
    # Hack - refresh auth.user so that if ipn notification has come in 
    # the background, we can refresh the outstanding balance
    auth.user = Storage(db.auth_user._filter_fields(db.auth_user[auth.user.id], id=True))
    session.auth.user = auth.user

    if auth.user.paid:
        session.flash='You have no balance'
        redirect(URL('index'))

    auth_user, users, balance, balances = cart_details(db=db, auth_user_id=auth.user.id, 
        settings=settings)
    if not auth_user.payment_invoice:
        auth_user.update_record(payment_invoice=str(uuid.uuid1()))
    
    form = SQLFORM.factory(Field('cheque', 'string', requires=IS_NOT_EMPTY()),
        formstyle='ul')
    if form.accepts(request.vars, session):
        auth_user.update_record(cheque=form.vars.cheque)
        mail.send(to=auth.user.email, bcc='abhayashenoy@gmail.com', 
            message=settings.cheque_email % (dict(first_name=auth.user.first_name,
                last_name=auth.user.last_name, payment_amount=balance)),
            subject=settings.cheque_subject)
        redirect(URL('payment_processed', args=['chq']))

    paypal_vars = {}
    i = 1;
    for b in balances:
        paypal_vars['item_name_%d' % i] = b.name
        paypal_vars['amount_%d' % i] = b.conf
        if b.disc:
            paypal_vars['discount_amount_%d' % i] = b.disc
        i += 1
        for t in b.tuts:
            paypal_vars['item_name_%d' % i] = t
            paypal_vars['amount_%d' % i] = settings.tutorial_rate
            i += 1

    tracker = str(uuid.uuid1())
    auth_user.update_record(paypal_tracker=tracker)
    paypal_form = paypal.PayPal(request=request, settings=settings, custom=tracker, **paypal_vars).encrypted_form()
    return dict(form=form, balance=balance, balances=balances, paypal_form=paypal_form)

def list_talks():
    papers=db(db.paper.status=='Accepted').select(orderby=db.paper.section|db.paper.authors)
    return dict(papers=papers)

def show_talk():
    paper=get(db.paper)
    return dict(papers=papers)

@auth.requires(auth.user and auth.user.manager)
def manage_talks():
    db.paper.authors.default = '%(first_name)s %(last_name)s' % auth.user
    form=crud.create(db.paper,next='manage_talk/[id]')
    papers_all = db(db.paper.id!=auth.user_id).select() if editor else []
    papers_mine = db(db.paper.created_by==auth.user_id).select()
    papers_to_review =db(db.paper.id.belongs(db(db.assignment.reviewer==auth.user_id)._select(db.assignment.id))).select()
    return dict(papers_all=papers_all,papers_mine=papers_mine,papers_to_review=papers_to_review, form=form)

@auth.requires(auth.user and auth.user.manager)
def manage_talk():
    paper = get(db.paper)
    author = paper.created_by==auth.user_id
    manager = auth.user.manager
    crud.messages.submit_button = 'Save'
    edit_form=crud.update(db.paper,paper,next=URL(r=request,args=paper.id)) if author or manager else None
    reviewer = db(db.assignment.paper==paper.id)(db.assignment.reviewer==auth.user_id).count()
    add_reviewer_form,reviewers=None, None
    if author:
        types=AUTHOR_MESSAGE_TYPE
    elif editor:
        db.assignment.paper.default=paper.id
        crud.messages.submit_button = 'Add'
        add_reviewer_form=crud.create(db.assignment)
        reviewers=db(db.auth_user.id.belongs(db(db.assignment.paper==paper.id)\
                                                 ._select(db.assignment.reviewer))).select()
        types=EDITOR_MESSAGE_TYPE
        for reviewer in reviewers:
            types.append((reviewer.id+1000,'Message to %s' % reviewer.first_name + ' ' + reviewer.last_name))
    elif reviewer:
        types=REVIEWER_MESSAGE_TYPE
    else:
        redirect(URL('manage_papers'))        
    db.message.message_type.requires=IS_IN_SET(types,zero=None)
    def email_users(form):
        k = int(form.vars.message_type)
        if k==11:
            paper.update_record(file=form.vars.file,status=paper.status+' S:')
        elif k==23:
            paper.update_record(status='Accepted')
        elif k==24:
            paper.update_record(status='Conditionally Accepted')
        elif k==25:
            paper.update_record(status='Rejected')
        elif k == 32:
            paper.update_record(status=paper.status+'A')
        elif k == 33:
            paper.update_record(status=paper.status+'C')
        elif k == 34:
            paper.update_record(status=paper.status+'R')
        message=form.vars.body
        subject=MESSAGE_TYPES.get(k,'Private Communication')
        if k in AUTHOR_MESSAGE_POLICY:
            to=paper.created_by.email
        elif k in EDITOR_MESSAGE_POLICY:
            to=[x.email for x in db(db.auth_user.editor==True).select(db.auth_user.email)]
        elif k in REVIEWER_MESSAGE_POLICY:
            to=[x.email for x in db(db.auth_user.id.belongs(db(db.assignment.paper==paper.id)\
              ._select(db.assignment.reviewer))).select(db.auth_user.email)]            
        elif k>1000:
            to=db(db.auth_user.id==k-1000).select().first().email
        else:
            return
        mail.send(to=to, bcc='abhayashenoy@gmail.com', message=message,subject=subject)
    db.message.paper.default=paper.id
    crud.messages.submit_button = 'Send'
    form=crud.create(db.message,onaccept=email_users)
    messages=db(db.message.paper==paper.id).select(orderby=db.message.created_on)
    return dict(paper=paper,author=author,reviewer=reviewer,manager=manager,form=form,
                messages=messages,edit_form=edit_form,add_reviewer_form=add_reviewer_form,reviewers=reviewers)

def venue(): return dict()

@auth.requires(auth.user and auth.user.manager)
def slideshow():
    db.slideshow.id.represent=lambda id: A('[edit]',_href=URL(args=id))
    db.slideshow.image.represent=lambda x: IMG(_src=URL('download',args=x),_width="100px")
    form=crud.update(db.slideshow,request.args(0))
    images=SQLTABLE(db(db.slideshow.id>0).select(),headers='fieldname:capitalize')
    return dict(form=form,images=images)

@auth.requires(auth.user and auth.user.manager)
def manage_users():
    db.auth_user.registered_by.default=auth.user.id
    record=db.auth_user(request.args(0) or 0)
    if record:
        crud.messages.submit_button = 'Save'
    else:
        crud.messages.submit_button = 'Add'
    form=crud.update(db.auth_user,
                     record,
                     message='User registered')
    return dict(form=form)

@auth.requires(request.args(0) != 'register')
def user():
    """
    exposes:
    http://..../[app]/default/user/login 
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    if request.args(0)=='profile' and auth.user and auth.user.paid:
        db.auth_user.rate.writable=False
        db.auth_user.tutorials.writable=False
    if request.args(0) == 'profile':
        auth.messages.submit_button = 'Save'
    elif request.args(0) == 'register':
        auth.messages.submit_button = 'Register'
    elif request.args(0) == 'login':
        auth.messages.submit_button = 'Login'
    elif request.args(0) == 'retrieve_password':
        auth.messages.submit_button = 'Retrieve Password'
    elif request.args(0) == 'change_password':
        auth.messages.submit_button = 'Change Password'
    elif request.args(0) == 'request_reset_password':
        auth.messages.submit_button = 'Reset'
    return dict(form=auth())


def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request,db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    session.forget()
    return service()

@auth.requires(auth.user and auth.user.manager)
def reports():
    paid = (db.auth_user.paid==True)
    not_paid = (db.auth_user.paid==False)
    ordinary = (db.auth_user.guest==False) & (db.auth_user.speaker==False)
    guest = (db.auth_user.guest==True)
    speaker = (db.auth_user.speaker==True)

    tutorial_counts = {}
    for i in range(1, len(settings.tutorials) + 1):        
        tutorial_counts[settings.tutorials[i - 1][1]] = (db(paid & (db.auth_user.tutorials.contains('00%s' % i))).count(),
            db(not_paid & (db.auth_user.tutorials.contains('00%s' % i))).count(),
            settings.tutorials[i - 1][0])

    food = {}
    for i in settings.food_prefs:
        food[i] = (db(paid & (db.auth_user.dietary_preferences==i)).count(),
            db(not_paid & (db.auth_user.dietary_preferences==i)).count())

    tshirts = {}
    for i in settings.tshirt_sizes:
        tshirts[i] = (db(paid & (db.auth_user.tshirt==i)).count(),
            db(not_paid & (db.auth_user.tshirt==i)).count())

    sg = (db(paid & (db.auth_user.country=='Singapore')).count(), db(not_paid & (db.auth_user.country=='Singapore')).count())
    others = (db(paid & (db.auth_user.country!='Singapore')).count(), db(not_paid & (db.auth_user.country!='Singapore')).count())
    
    totals = dict(all=(db(paid).count(), db(not_paid).count()),
        guest=(db(paid)(guest).count(), db(not_paid)(guest).count()),
        speaker=(db(paid)(speaker).count(), db(not_paid)(speaker).count()),
        ordinary=(db(paid)(ordinary).count(), db(not_paid)(ordinary).count()))
        
    return dict(totals=totals, tutorial_counts=tutorial_counts,
        food=food, tshirts=tshirts, sg=sg, others=others)

@auth.requires(auth.user and auth.user.manager)
def badges():
    users = db(db.auth_user.paid==True).select(db.auth_user.nick, db.auth_user.badge_1, db.auth_user.badge_2)
    return dict(users=users)

@auth.requires(auth.user and auth.user.manager)
def search_users():
    form, users = crud.search(db.auth_user,
        fields=(db.auth_user.first_name, db.auth_user.last_name, 
            db.auth_user.email, db.auth_user.rate, 
            db.auth_user.co, db.auth_user.country, db.auth_user.nick, 
            db.auth_user.badge_1, db.auth_user.badge_2))
    return dict(form=form, users=users)

@auth.requires(auth.user and auth.user.manager)
def manage_coupons():
    form, form_multi, form_email = None, None, None
    record = db.coupon(request.args(0) or 0)
    if record:
        crud.messages.submit_button = 'Save'
        form = crud.update(db.coupon,
            record,
            message='Coupon created')
        if not record.used:
            form_email = SQLFORM.factory(Field('user', 
                    requires=IS_EMPTY_OR(IS_IN_DB(db, 'auth_user.id',
                        label=lambda r: "%s %s" %(r.first_name, r.last_name)))),
                Field('email', requires=IS_EMPTY_OR(IS_EMAIL())),
                Field('coupon_id', default=record.id, readable=False, writable=False),
                formstyle='ul', submit_button='Send')
            if form_email.accepts(request.vars, session, keepvalues=True):
                if form_email.vars.user is None and form_email.vars.email is None:
                    form_email.errors.user = 'Please choose a user or enter an email address'
                else:
                    if form_email.vars.user:
                        to = db.auth_user[int(form_email.vars.user)].email
                        message = settings.coupon_email_greeting_user % db.auth_user[int(form_email.vars.user)]
                    else:
                        to = form_email.vars.email
                        message = settings.coupon_email_greeting_generic
                    message +=  settings.coupon_email_code
                    message +=  settings.coupon_email_footer
                    message = message % record
                    mail.send(to=to, bcc='abhayashenoy@gmail.com', message=message, subject=settings.coupon_subject)
                    response.flash = 'Email sent'
                    form_email.accepts(request.vars, session)
    else:
        form_multi = SQLFORM.factory(Field('num', 'integer', label='Number of coupons to create', requires=IS_INT_IN_RANGE(1, None)),
            Field('amount', 'double', label='Discount amount', requires=IS_NOT_EMPTY()),
            Field('desc', 'text', label='Description'),
            Field('user',
                    requires=IS_EMPTY_OR(IS_IN_DB(db, 'auth_user.id',
                        label=lambda r: "%s %s" %(r.first_name, r.last_name)))),
            Field('email', 'string', requires=IS_EMPTY_OR(IS_EMAIL())),
            formstyle='ul', submit_button='Create')
        if form_multi.accepts(request.vars, session, keepvalues=True):
            if form_multi.vars.user is None and form_multi.vars.email is None:
                form_multi.errors.user = 'Please choose a user or enter an email address'
            else:
                coupons_new = []
                for i in xrange(0, form_multi.vars.num):
                    coupons_new.append(db.coupon.insert(code=str(uuid.uuid1()), 
                        description=form_multi.vars.desc, amount=form_multi.vars.amount))
                db.commit()
                if form_multi.vars.user:
                    to = db.auth_user[int(form_multi.vars.user)].email
                    message = settings.coupon_email_greeting_user % db.auth_user[int(form_multi.vars.user)]
                else:
                    to = form_multi.vars.email
                    message = settings.coupon_email_greeting_generic
                if form_multi.vars.num > 1:
                    message += settings.coupon_email_codes % dict(num=form_multi.vars.num, 
                        code='\n'.join([db.coupon[id].code for id in coupons_new]),
                        amount=form_multi.vars.amount)
                else:
                    message +=  settings.coupon_email_code % db.coupon[coupons_new[0]]
                message +=  settings.coupon_email_footer
                mail.send(to=to, bcc='abhayashenoy@gmail.com', message=message, subject=settings.coupon_subject)
                response.flash = 'Email sent'
                form_multi.accepts(request.vars, session)
    return dict(form=form, form_email=form_email, form_multi=form_multi)

@auth.requires(auth.user and auth.user.manager)
def users():
    users=plugin_wiki.widget('jqgrid',table='auth_user',
        fields=['id', 'first_name', 'last_name', 'email', 'registered', 'payment_amount'],
        width=650, height=1400,
        col_widths='45,120,120,200,70,90')
    return dict(users=users)

@auth.requires(auth.user and auth.user.manager)
def coupons():
    coupons = plugin_wiki.widget('jqgrid', table='coupon',
        fields=('id', 'code', 'amount', 'created_by'),
        width=500, height=300,
        col_widths='45,250,70,120')
    return dict(coupons=coupons)

@auth.requires_login()
def payment_processed():
    return dict(request.vars)

def ipn():
    query = request.body.read()
    params = request.post_vars
    if not query or not params.txn_id:
        return dict()

    duplicate = False
    id = db.paypal_txns.insert(txn_id=params.txn_id, ipn_vars=query, 
        tracker=params.custom, status=params.payment_status)
    if db((db.paypal_txns.tracker==params.custom) & (db.paypal_txns.status!='Completed')).count() > 1:
        duplicate = True
        print 'Duplicate IPN notification %s, db row id %s' % (query, id)
        mail.send(to=setting.administrator, subject='Duplicate IPN transaction',
            message=settings.invalid_ipn_email % (params.custom, query, id))

    try:
        url = settings.paypal_url + '?cmd=_notify-validate&' + query
        response = urlopen(url)
        resp = response.read().lower()
    except URLError:
        print 'Could not check IPN notification validity'
        return dict()
    if resp != 'verified' or duplicate:
        print 'invalid or duplicate IPN notification'
        return dict()

    user = db(db.auth_user.paypal_tracker==params.custom).select().first()
    if not user:
        print 'Unknown tracker id', params.custom
        return
    
    s_user, other_users, balance, balances = cart_details(db=db, s_user=user,
        settings=settings)
    if float(params.mc_gross) != float(balance) or \
        params.payment_status != 'Completed' or \
        params.mc_currency != 'SGD' or \
        params.business != settings.paypal_business_email:
        print 'Invalid IPN notification %s, db row id %s' % (query, id)
        mail.send(to=settings.administrator, subject='Invalid IPN transaction',
            message=settings.invalid_ipn_email % (params.custom, query, id))
        return
    
    print 'IPN notification tracker', params.custom
    for u in itertools.chain([s_user,], other_users):
        u.update_record(paid=True, payment_datetime=request.now)

@auth.requires_login()
def invoice():
    if auth.user.paid:
        session.flash='You have no balance'
        redirect(URL('index'))

    auth_user, users, balance, balances = cart_details(db=db, auth_user_id=auth.user.id,
        settings=settings)
    
    if not auth_user.payment_invoice:
        auth_user.update_record(payment_invoice=str(uuid.uuid1()))
    return dict(balance=balance, balances=balances, user=auth_user)

@auth.requires_login()
def receipt():
    if not auth.user.paid:
        session.flash='You have not yet checked out'
        redirect(URL('index'))

    auth_user, users, balance, balances = cart_details(db=db, auth_user_id=auth.user.id,
        q=db(db.auth_user.registered_by==auth.user.id), settings=settings)
    return dict(balance=balance, balances=balances, user=auth_user)

@auth.requires(auth.user and auth.user.manager)
def invoice_for():
    response.view = 'default/invoice.html'
    auth_user, users, balance, balances = cart_details(db=db, auth_user_id=request.args(0),
        settings=settings)
    
    return dict(balance=balance, balances=balances, user=auth_user)

@auth.requires(auth.user and auth.user.manager)
def not_paid():
    return dict(users=db(db.auth_user.paid==False).select())

@auth.requires(auth.user and auth.user.manager)
def cheque_payment():
    response.view = 'default/not_paid.html'
    return dict(users=db((db.auth_user.cheque!='') & (db.auth_user.paid==False)).select())

@auth.requires(auth.user and auth.user.manager)
def users_filtered():
    queries = []
    if 'paid' in request.vars:
        if request.vars['paid'].lower() == 'true':
            queries.append(db.auth_user.paid==True)
        else:
            queries.append(db.auth_user.paid==False)
    if 'tutorial' in request.vars:
        queries.append(db.auth_user.tutorials.contains(request.vars['tutorial']))
    if 'who' in request.vars:
        if request.vars['who'] == 'sg':
            queries.append(db.auth_user.country=='Singapore')
        else:
            queries.append(db.auth_user.country!='Singapore')
    if 'type' in request.vars:
        t = request.vars['type']
        if t == 'guest':
            queries.append(db.auth_user.guest==True)
        elif t == 'speaker':
            queries.append(db.auth_user.speaker==True)
        else:
            queries.append((db.auth_user.guest==False) & (db.auth_user.speaker==False))
            
    if queries:
        res = db(queries[0])
        for q in queries[1:]:
            res = res(q)
    else:
        res = db()
    res = res.select(db.auth_user.first_name, db.auth_user.last_name, db.auth_user.email)
    return dict(users=res)

@auth.requires(auth.user and auth.user.manager)
def user_update():
    def _checked(field):
        if field:
            return dict(value=True)
        return dict()
    if request.post_vars:
        for id in request.post_vars:
            flags = request.post_vars[id]
            id = int(id)
            db(db.auth_user.id==id).update(
                speaker=('speaker' in flags), 
                guest=('guest' in flags))
            response.flash='Updated users!'

    rows = []
    for u in db(db.auth_user.id>0).select():
        rows.append((A(u.first_name + ' ' + u.last_name, _href='http://localhost:8080/appadmin/update/db/auth_user/%s' % u.id), 
            INPUT(_type='checkbox', _name=u.id, _value='speaker', **_checked(u.speaker)),
            INPUT(_type='checkbox', _name=u.id, _value='guest', **_checked(u.guest)),
            INPUT(_type='hidden', _name=u.id, _value='force')))

    form = FORM(TABLE(TR('', 'Speaker', 'Guest'), *[TR(r) for r in rows]),
        INPUT(_type="submit", _value='Update', _class="button"), 
        _action='', _method='post', _enctype='application/x-www-form-urlencoded')
    return dict(form=form)

@auth.requires(auth.user and auth.user.manager)
def import_csv():
    form = FORM(INPUT(_type='file', _name='data'), INPUT(_type='submit'))
    if form.accepts(request.vars):
        lines = request.vars.data.file.readlines()
        users = [l.strip().split(',') for l in lines]
        for user in users:
            u = map(lambda x: x.strip(), user)
            db.auth_user.insert(
                first_name=u[0],
                last_name=u[1],
                email=u[2],
                phone=u[3],
                dietary_preferences=u[4],
                tutorials=['%03d' % int(x) for x in (u[5], u[6]) if x],
                co=u[7],
                guest=True,
                paid=True,
                country='Singapore'
                )
        response.flash = 'Imported successfully'
    return dict(form=form)

def feedback():
    return dict()

def feedback_conf():
    return dict()

def feedback_tut():
    return dict()