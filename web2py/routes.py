#!/usr/bin/python
# -*- coding: utf-8 -*-

# default_application, default_controller, default_function
# are used when the respective element is missing from the
# (possibly rewritten) incoming URL
#
default_application = 'pycon'    # ordinarily set in base routes.py
default_controller = 'default'  # ordinarily set in app-specific routes.py
default_function = 'index'      # ordinarily set in app-specific routes.py

# routes_app is a tuple of tuples.  The first item in each is a regexp that will
# be used to match the incoming request URL. The second item in the tuple is
# an applicationname.  This mechanism allows you to specify the use of an
# app-specific routes.py. This entry is meaningful only in the base routes.py.
#
# Example: support welcome, admin, app and myapp, with myapp the default:


routes_app = ((r'/(?P<app>|admin|pycon)\b.*', r'\g<app>'),
              (r'(.*)', 'pycon'),
              (r'/?(.*)', r'pycon'))

# routes_in is a tuple of tuples.  The first item in each is a regexp that will
# be used to match the incoming request URL. The second item in the tuple is
# what it will be replaced with.  This mechanism allows you to redirect incoming
# routes to different web2py locations
#
# Example: If you wish for your entire website to use init's static directory:
#
#   routes_in=( (r'/static/(?P<file>[\w./-]+)', r'/init/static/\g<file>') )
#

routes_in = (
    (r'/admin$anything', r'/admin$anything'),
    (r'/blog$anything', r'/blog$anything'),
    ('/d$anything', '/pycon/default$anything'),
    ('/w$anything', '/pycon/plugin_wiki$anything'),
    ('/(?P<any>.*)', '/pycon/\g<any>'),
    (r'.*:/favicon.ico', r'/pycon/static/favicon.ico'),
    (r'.*:/robots.txt', r'/pycon/static/robots.txt')
)

# routes_out, like routes_in translates URL paths created with the web2py URL()
# function in the same manner that route_in translates inbound URL paths.
#

routes_out = (
    (r'/pycon/default$anything', r'/d$anything'),
    (r'/pycon/plugin_wiki$anything', r'/w$anything'),
    (r'/pycon(?P<any>.*)', r'\g<any>'),
)

# Error-handling redirects all HTTP errors (status codes >= 400) to a specified
# path.  If you wish to use error-handling redirects, uncomment the tuple
# below.  You can customize responses by adding a tuple entry with the first
# value in 'appName/HTTPstatusCode' format. ( Only HTTP codes >= 400 are
# routed. ) and the value as a path to redirect the user to.  You may also use
# '*' as a wildcard.
#
# The error handling page is also passed the error code and ticket as
# variables.  Traceback information will be stored in the ticket.
#
routes_onerror = [
    (r'*/404', r'/w/page/404'),
#    (r'*/*', r'/w/page/error'),
]

# specify action in charge of error handling
#
# error_handler = dict(application='error',
#                      controller='default',
#                      function='index')

# In the event that the error-handling page itself returns an error, web2py will
# fall back to its old static responses.  You can customize them here.
# ErrorMessageTicket takes a string format dictionary containing (only) the
# "ticket" key.

# error_message = '<html><body><h1>Invalid request</h1></body></html>'
# error_message_ticket = '<html><body><h1>Internal error</h1>Ticket issued: <a href="/admin/default/ticket/%(ticket)s" target="_blank">%(ticket)s</a></body></html>'

# specify a list of apps that bypass args-checking and use request.raw_args
#
#routes_apps_raw=['myapp']
#routes_apps_raw=['myapp', 'myotherapp']
