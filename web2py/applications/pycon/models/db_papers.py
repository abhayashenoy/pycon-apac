AUTHOR_MESSAGE_TYPE=[(11,'Paper Upload/Resubmission'),
                     (12,'General Communication')]

EDITOR_MESSAGE_TYPE=[(21,'Message to author and reviewers'),
                     (22,'Review Assignment'),
                     (23,'Notification of Acceptance'),
                     (24,'Notification of Conditional Acceptance'),
                     (25,'Notification of Rejection'),
                     (26,'Message to all reviewers'),
                     (32,'Review Submitted: Accept'),
                     (33,'Review Submitted: Conditional Accept'),
                     (34,'Review Submitted: Reject')]


REVIEWER_MESSAGE_TYPE=[(31,'General Communication'),
                       (32,'Review Submitted: Accept'),
                       (33,'Review Submitted: Conditional Accept'),
                       (34,'Review Submitted: Reject'),
                       (35,'Message to the editor')]

#MESSAGE_TYPE 1034, 'Private Editor-Reviewer Communication' to reviewer 10234-34 = #34

AUTHOR_MESSAGE_POLICY=(11,21,23,24,25,31,32,33,34)
EDITOR_MESSAGE_POLICY=(11,12,31,32,33,34,35)
REVIEWER_MESSAGE_POLICY=(12,21,22,26)
PRIVACY_POLICY=lambda x: x in (26,36) or x>1000
MESSAGE_TYPES=dict(item for item in AUTHOR_MESSAGE_TYPE+EDITOR_MESSAGE_TYPE+REVIEWER_MESSAGE_TYPE)

created_by=Field('created_by',db.auth_user,default=auth.user_id,writable=False,readable=False)
created_on=Field('created_on','datetime',default=request.now,writable=False,readable=False)

db.define_table('paper',
                Field('section','string',writable=False,readable=False,default=settings.sections[0],
                      requires=IS_IN_SET(settings.sections)),
                Field('title', requires=IS_NOT_EMPTY(error_message='Enter a title for your talk')),
                Field('authors', label='Presenters', 
                    requires=IS_NOT_EMPTY(error_message='Enter the names of the presenters ')),
                Field('abstract', 'text', 
                    requires=IS_NOT_EMPTY(error_message='Enter a brief description'),
                    label='Brief description'),
                Field('bio', 'text', label='Presenter Bio'),
                Field('tags', 'string'),
                Field('difficulty', 'string', default=settings.difficulty[0],
                    requires=IS_IN_SET(settings.difficulty,
                        error_message='Choose a difficulty level'),
                    label='Difficulty level'),
                Field('recording', 'string', default=settings.permissions[0],
                    requires=IS_IN_SET(settings.permissions,
                        error_message='Tell us whether we can record your talk'),
                    label='Can we record your talk ?'),
                Field('status',default='Pending Approval',writable=False,readable=False),
                Field('file','upload',writable=False, readable=False),
                Field('country', 'string'),
                created_by, created_on,
                format='%(title)s')

db.define_table('assignment',
                Field('paper',db.paper,writable=False,readable=False),
                Field('reviewer',db.auth_user),
                created_by, created_on)

db.define_table('message',
                Field('paper',db.paper,writable=False,readable=False),
                Field('message_type','integer',label='Action',requires=IS_IN_SET(MESSAGE_TYPES)),
                Field('body','text',label='Message'),
                Field('file','upload'),
                created_by, created_on)
                
from gluon.contrib.populate import populate
if not settings.production and db(db.auth_user.id>0).count()==1:
    populate(db.auth_user,25)
    populate(db.paper,25)
    db(db.paper.id>0).update(status='Accepted',created_by=2)
    populate(db.assignment,75)
    populate(db.message,200)
