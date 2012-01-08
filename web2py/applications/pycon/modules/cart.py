import itertools
from gluon.storage import Storage

def cart_details(db=None, s_user=None, auth_user_id=None, q=None,
    settings=None):
    if not s_user:
        s_user = db.auth_user[auth_user_id]
    if q:
        users = q.select()
    else:
        users=db(db.auth_user.registered_by==s_user.id)\
            (db.auth_user.paid==False).select()

    total = s_user.payment_amount + sum(x.payment_amount for x in users)

    tuts = dict(settings.tutorials)
    rates = dict([(x[0], x[4]) for x in settings.rates])
    balances = []
    for user in itertools.chain([s_user,], users):
        disc = db(db.coupon.code==user.discount_coupon).select()
        if len(disc):
            disc = disc[0].amount
        name = "Conference fee for %(first_name)s %(last_name)s" % user
        balances.append(Storage(name=name,
            conf=rates[user.rate], tuts=[tuts[t] for t in user.tutorials],
            disc=disc, id=user.id))

    return (s_user, users, total, balances) 