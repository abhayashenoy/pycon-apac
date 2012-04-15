# -*- coding: utf-8 -*- 

_b = Storage()
if request and request.wsgi and request.wsgi.environ:
    path = request.wsgi.environ['PATH_INFO']
    for p in ('conference', 'tutorials', 'tournament', 'talks', 'schedule', 'venue', 'participants', 'faq', 'index'):
        if path.endswith(p):
            _b[p] = True
            break

    if path == '/pycon/':
        _b['index'] = True

response.menu = [
    [T('About'),        _b.index or False,          URL(request.application,'default','index'),               []],
    [T('Conference'),   _b.conference or False,     URL(request.application,'plugin_wiki','page/conference'), []],
    [T('Tutorials'),    _b.tutorials or False,      URL(request.application,'plugin_wiki','page/tutorials'),  []],
    [T('Tournament'),   _b.tournament or False,     URL(request.application,'plugin_wiki','page/tournament'), []],
    [T('Talks'),        _b.talks or False,          URL(request.application,'default','list_talks'),          []],
    [T('Schedule'),     _b.schedule or False,       URL(request.application,'default','schedule'),            []],
    [T('Venue'),        _b.venue or False,          URL(request.application,'default','venue'),      []],
    [T('FAQ'),          _b.faq or False,            URL(request.application,'plugin_wiki','page/faq'),        []],
   ]

