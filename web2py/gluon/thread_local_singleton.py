import threading

class Singleton(dict):
    """
    This class makes a thread local Singleton
    (i.e. every threads sees a differnt singleton)
    It also makes a different singleton for each derived class.
    The objects behave like dictionaries and attributes/values
    are mapped into keys/values.
    But, while if not 'x' in a, a['x'] raises and exception a.x returns None
    Example:

    >>> a=Singleton()
    >>> a.x=1
    >>> b=Singleton() # same singleton as a
    >>> print b.x
    1
    >>> class C(Singleton): pass
    >>> c=C()         # new singleton
    >>> c.y=2
    >>> d=C()         # same singleton as c
    >>> print d.x, d.y
    None, 2
    >>> d.set_state({}) # state can be reset
    >>> print d.x, d.y
    None None
    """
    thread = threading.local()
    def __init__(self):
        if not hasattr(Singleton.thread,str(self.__class__)):
            setattr(Singleton.thread,str(self.__class__),{})
    def __getitem__(self,key):
        return getattr(Singleton.thread,str(self.__class__))[key]
    def __setitem__(self,key,value):
        getattr(Singleton.thread,str(self.__class__))[key]=value
    def __setattr__(self,key,value):
        getattr(Singleton.thread,str(self.__class__))[key]=value
    def __delattr__(self,key):
        del getattr(Singleton.thread,str(self.__class__))[key]
    def get(self,key,value):
        return getattr(Singleton.thread,str(self.__class__)).get(key,value)
    def __getattr__(self,key):
        return getattr(Singleton.thread,str(self.__class__)).get(key,None)
    def __repr__(self):
        return '<Storage ' + repr(getattr(Singleton.thread,str(self.__class__))) + '>'
    def __str__(self):
        return str(getattr(Singleton.thread,str(self.__class__)))
    def __getstate__(self):
        return getattr(Singleton.thread,str(self.__class__))
    def __setstate__(self, value):
        setattr(Singleton.thread,str(self.__class__),value)
    def __cmp__(self,other):
        return 0
    def __contains__(self,value):
        return value in getattr(Singleton.thread,str(self.__class__))
    def __hash__(self):
        return hash(getattr(Singleton.thread,str(self.__class__)))
    def __len__(self):
        return len(getattr(Singleton.thread,str(self.__class__)))
    def has_key(self,key):
        return key in self
    def keys(self):
        return getattr(Singleton.thread,str(self.__class__)).keys()
    def values(self):
        return getattr(Singleton.thread,str(self.__class__)).values()
    def items(self):
        return getattr(Singleton.thread,str(self.__class__)).items()
    def iterkeys(self):
        return getattr(Singleton.thread,str(self.__class__)).iterkeys()
    def itervalues(self):
        return getattr(Singleton.thread,str(self.__class__)).itervalues()
    def iteritems(self):
        return getattr(Singleton.thread,str(self.__class__)).iteritems()
    def update(self,*a,**b):
        return getattr(Singleton.thread,str(self.__class__)).update(*a,**b)
    def popitem(self):
        return getattr(Singleton.thread,str(self.__class__)).popitem()
    def clear(self):
        return getattr(Singleton.thread,str(self.__class__)).clear()
    def copy(self):
        return getattr(Singleton.thread,str(self.__class__)).copy()
    def __iter__(self):
        return getattr(Singleton.thread,str(self.__class__)).__iter__()
    def get_state(self):
        return getattr(Singleton.thread,str(self.__class__))
    def set_state(self,storage):
        setattr(Singleton.thread,str(self.__class__),storage)

