db.define_table('slideshow',
                Field('active','boolean',default=True),
                Field('image','upload',requires=IS_NOT_EMPTY()),
                Field('caption',requires=IS_NOT_EMPTY()))
