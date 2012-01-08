import uuid

db.define_table('coupon',
                Field('code',default=str(uuid.uuid1())),
                Field('description','text'),
                Field('amount','double', label='Discount amount', requires=IS_NOT_EMPTY()),
                Field('created_by', db.auth_user, default=auth.user_id, writable=False),
                Field('created_on', 'datetime', default=request.now, writable=False, readable=False),
                Field('used', 'boolean', default=False, writable=False, readable=False),
                Field('used_by', db.auth_user, writable=False, readable=False, default=None),
                Field('used_on','datetime', writable=False, readable=False))

db.coupon.id.represent=lambda id: A(id,_href=URL('default','manage_coupons',args=id), _target='_top')
db.coupon.created_by.represent=lambda id: A("%s %s" % (db.auth_user[id].first_name, db.auth_user[id].last_name), _href=URL('default','manage_users',args=id), _target='_top')
