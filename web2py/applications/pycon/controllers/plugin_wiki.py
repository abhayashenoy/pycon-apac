# This file was developed by Massimo Di Pierro
# It is released under BSD, MIT and GPL2 licenses

##########################################################
# code to handle wiki pages
##########################################################

@auth.requires(plugin_wiki_editor)
def index():
    w = db.plugin_wiki_page
    if plugin_wiki_editor:
        pages = db(w.id>0).select(orderby=w.slug)
    else:
        pages = db(w.active==True)(w.public==True).select(orderby=w.slug)
    if plugin_wiki_editor:
        form=SQLFORM.factory(Field('slug',requires=db.plugin_wiki_page.slug.requires),
                             Field('from_template',requires=IS_EMPTY_OR(IS_IN_DB(db,db.plugin_wiki_page.slug))),
                             formstyle='ul')
        if form.accepts(request.vars):
            redirect(URL(r=request,f='page',args=form.vars.slug,vars=dict(template=request.vars.from_template or '')))
    else:
        form=''
    return dict(pages=pages,form=form)

def page():
    """
    shows a page
    """
    slug = request.args(0) or 'index'
    w = db.plugin_wiki_page
    page = db(w.slug==slug).select().first()
    if not auth.user and (not page or not page.public or not page.active):
        redirect(URL(r=request,c='default',f='user',args='login'))
    elif not plugin_wiki_editor and (not page or not page.public or not page.active):
        raise HTTP(404)
    elif page and page.role and not auth.has_membership(page.role):    
        raise HTTP(404)
    if request.extension=='load':
        return plugin_wiki.render(page.body)
    if request.extension=='html':         
        return dict(page=page,slug=slug)
    return MARKMIN(page.body,extra={'widget':(lambda code:''),
                                    'template':(lambda template:'')})

def page_archive():
    """
    shows and old version of a page
    """
    id = request.args(0)
    h = db.plugin_wiki_page_archive
    page = db(h.id==id).select().first()
    if not page or (not plugin_wiki_editor and (not page.public or not page.active)):
        raise HTTP(404)
    elif page and page.role and not auth.has_membership(page.role):
        raise HTTP(404)
    if request.extension!='html': return page.body
    return dict(page=page)

@auth.requires(plugin_wiki_editor)
def page_edit():
    """
    edit a page
    """
    slug = request.args(0) or 'index'
    w = db.plugin_wiki_page
    w.role.writable = w.role.readable = plugin_wiki_level>1
    page = db(w.slug==slug).select().first() 
    if not page:
        page = w.insert(slug=slug, 
                        title=slug.replace('-',' ').capitalize(),
                        body=request.vars.template and w(slug=request.vars.template).body or '')
    form = crud.update(w, page, onaccept=crud.archive,
                       next=URL(r=request,f='page',args=request.args))
    return dict(form=form,page=page)

def page_history():
    """
    show page changelog
    """
    slug = request.args(0) or 'index'
    w = db.plugin_wiki_page
    h = db.plugin_wiki_page_archive
    page = db(w.slug==slug).select().first()
    history = db(h.current_record==page.id).select(orderby=~h.modified_on)
    return dict(page=page, history=history)


##########################################################
# ajax callbacks
##########################################################
@auth.requires_login()
def attachments():
    """
    allows to edit page attachments
    """
    a=db.plugin_wiki_attachment
    a.tablename.default=tablename=request.args(0)
    a.record_id.default=record_id=request.args(1)
    #if request.args(2): a.file.writable=False
    form=crud.update(a,request.args(2),
                     next=URL(r=request,args=request.args[:2]))
    if request.vars.list_all:
        query = a.id>0
    else:
        query = (a.tablename==tablename)&(a.record_id==record_id)
    rows=db(query).select(orderby=a.name)
    return dict(form=form,rows=rows)

def attachment():
    """
    displays an attachments
    """
    a=db.plugin_wiki_attachment
    try:
        request.args[0]=a[request.args(0).split('.')[0]].file
    except:
        raise HTTP(400)
    return response.download(request,db)

def comment():
    """
    post a comment
    """
    tablename, record_id = request.args(0), request.args(1)
    table=db.plugin_wiki_comment
    if record_id=='None': record_id=0
    table.tablename.default=tablename
    table.record_id.default=record_id
    if auth.user:
        form = crud.create(table)
    else:
        form = A(T('login to comment',_href=auth.settings.login_url))
    comments=db(table.tablename==tablename)\
        (table.record_id==record_id).select()
    return dict(form = form,comments=comments)

@auth.requires_login()
def jqgrid():
    """
    jqgrid callback retrieves records
    http://trirand.com/blog/jqgrid/server.php?q=1&_search=false&nd=1267835445772&rows=10&page=1&sidx=amount&sord=asc&searchField=&searchString=&searchOper=
    """
    from gluon.serializers import json
    import cgi
    tablename = request.vars.tablename or error()
    columns = (request.vars.columns or error()).split(',')
    rows=int(request.vars.rows or 25)
    page=int(request.vars.page or 0)
    sidx=request.vars.sidx or 'id'
    sord=request.vars.sord or 'asc'
    searchField=request.vars.searchField
    searchString=request.vars.searchString
    searchOper={'eq':lambda a,b: a==b,
                'nq':lambda a,b: a!=b,
                'gt':lambda a,b: a>b,
                'ge':lambda a,b: a>=b,
                'lt':lambda a,b: a<b,
                'le':lambda a,b: a<=b,
                'bw':lambda a,b: a.like(b+'%'),
                'bn':lambda a,b: ~a.like(b+'%'),
                'ew':lambda a,b: a.like('%'+b),
                'en':lambda a,b: ~a.like('%'+b),
                'cn':lambda a,b: a.like('%'+b+'%'),
                'nc':lambda a,b: ~a.like('%'+b+'%'),
                'in':lambda a,b: a.belongs(b.split()),
                'ni':lambda a,b: ~a.belongs(b.split())}\
                [request.vars.searchOper or 'eq']
    table=db[tablename]
    if request.vars.fieldname:
        dbset = table._db(table[request.vars.fieldname]==request.vars.fieldvalue)
    else:
        dbset = table._db(table.id>0)
    if searchField: dbset=dbset(searchOper(table[searchField],searchString))
    orderby = table[sidx]
    if sord=='desc': orderby=~orderby
    limitby=(rows*(page-1),rows*page)
    fields = [table[f] for f in columns]
    records = dbset.select(orderby=orderby,limitby=limitby,*fields)
    nrecords = dbset.count()
    items = {}
    items['page']=page
    items['total']=int((nrecords+(rows-1))/rows)
    items['records']=nrecords
    readable_fields=[f.name for f in fields if f.readable]
    def f(value,fieldname):
        r = table[fieldname].represent
        if r: value=r(value)
        try: return value.xml()
        except: return cgi.escape(str(value))
    items['rows']=[{'id':r.id,'cell':[f(r[x],x) for x in readable_fields]} \
                       for r in records]
    return json(items)

def tags():
    import re
    db_tag = db.plugin_wiki_tag
    db_link = db.plugin_wiki_link
    table_name=request.args(0)
    record_id=request.args(1)
    if not auth.user_id:
        return ''
    form = SQLFORM.factory(Field('tag_name',requires=IS_SLUG()), formstyle='ul')
    if request.vars.tag_name:
        for item in request.vars.tag_name.split(','):
            tag_name = re.compile('\s+').sub(' ',item).strip()
            tag_exists = tag = db(db_tag.name==tag_name).select().first()
            if not tag_exists:
                tag = db_tag.insert(name=tag_name, links=1)
            link = db(db_link.tag==tag.id)\
                (db_link.table_name==table_name)\
                (db_link.record_id==record_id).select().first()
            if not link:
                db_link.insert(tag=tag.id,
                               table_name=table_name,record_id=record_id)
                if tag_exists:
                    tag.update_record(links=tag.links+1)
    for key in request.vars:
        if key[:6]=='delete':
            link_id=key[6:]
            link=db_link[link_id]
            del db_link[link_id]
            db_tag[link.tag] = dict(links=db_tag[link.tag].links-1)
    links = db(db_link.table_name==table_name)\
              (db_link.record_id==record_id).select()\
              .sort(lambda row: row.tag.name.upper())
    return dict(links=links, form=form)

def cloud():
    tags = db(db.plugin_wiki_tag.links>0).select(limitby=(0,20))
    if tags:
        mc = max([tag.links for tag in tags])
    return DIV(_class='plugin_wiki_tag_cloud',*[SPAN(A(tag.name,_href=URL(r=request,c='plugin_wiki',f='page',args=('tag',tag.id))),_style='font-size:%sem' % (0.8+1.0*tag.links/mc)) for tag in tags])

@auth.requires(plugin_wiki_editor)
def widget():
    """
    >> inspect.getargspec(PluginWikiWidgets.tags)
    (['table', 'record_id'], None, None, ('None', None))
    >>> dir(PluginWikiWidgets)
    """
    import inspect
    name=request.vars.name
    widgets = ['']+[item for item in dir(PluginWikiWidgets) if item[0]!='_']
    form=FORM(LABEL('Widget Name: '), SELECT(_name='name',value=name,
                     _onchange="jQuery(this).parent().submit()",
                     *widgets))
    widget_code=''
    if name in widgets: 
        a,b,c,d=inspect.getargspec(getattr(PluginWikiWidgets,name))
        a,d=a or [],d or []
        null = lambda:None
        d=[null]*(len(a)-len(d))+[x for x in d]
        ESC='x'
        fields = [Field(ESC+a[i],label=a[i],default=d[i]!=null and d[i] or '',
                        requires=(d[i]==null) and IS_NOT_EMPTY() or None,
                        comment=(d[i]==null) and 'required' or '') \
                      for i in range(len(a))]
        form_widget=SQLFORM.factory(hidden=dict(name=name),*fields,
            formstyle='ul')
        doc = getattr(PluginWikiWidgets,name).func_doc or ''
        if form_widget.accepts(request.vars):
            keys=['name: %s' % request.vars.name]
            for name in a:
                if request.vars[ESC+name]:
                    keys.append(name+': %s' % request.vars[ESC+name])
            widget_code=CODE('``\n%s\n``:widget' % '\n'.join(keys))
    else:
        doc=''
        form_widget=''
    return dict(form=form,form_widget=form_widget,doc=doc,
                widget_code=widget_code)
