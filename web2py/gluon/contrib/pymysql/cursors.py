import struct
import re

from err import Warning, Error, InterfaceError, DataError, \
             DatabaseError, OperationalError, IntegrityError, InternalError, \
            NotSupportedError, ProgrammingError

insert_values = re.compile(r'\svalues\s*(\(.+\))', re.IGNORECASE)

class Cursor(object):
    '''
    This is the object you use to interact with the database.
    '''
    def __init__(self, connection):
        '''
        Do not create an instance of a Cursor yourself. Call
        connections.Connection.cursor().
        '''
        from weakref import proxy
        self.connection = proxy(connection)
        self.description = None
        self.rownumber = 0
        self.rowcount = -1
        self.arraysize = 1
        self._executed = None
        self.messages = []
        self.errorhandler = connection.errorhandler
        self._has_next = None
        self._rows = ()

    def __del__(self):
        '''
        When this gets GC'd close it.
        '''
        self.close()

    def close(self):
        '''
        Closing a cursor just exhausts all remaining data.
        '''
        if not self.connection:
            return
        try:
            while self.nextset():
                pass
        except:
            pass

        self.connection = None

    def _get_db(self):
        if not self.connection:
            self.errorhandler(self, ProgrammingError, "cursor closed")
        return self.connection
    
    def _check_executed(self):
        if not self._executed:
            self.errorhandler(self, ProgrammingError, "execute() first")
    
    def setinputsizes(self, *args):
        """Does nothing, required by DB API."""
                  
    def setoutputsizes(self, *args):
        """Does nothing, required by DB API."""
                                  
    def nextset(self):
        ''' Get the next query set '''
        if self._executed:
            self.fetchall()
        del self.messages[:]
        
        if not self._has_next:
            return None
        connection = self._get_db()
        connection.next_result()
        self._do_get_result()
        return True

    def execute(self, query, args=None):
        ''' Execute a query '''
        from sys import exc_info
        
        conn = self._get_db()
        charset = conn.charset
        del self.messages[:]
        
        # this ordering is good because conn.escape() returns
        # an encoded string.
        if isinstance(query, unicode):
            query = query.encode(charset)

        if args is not None:
            query = query % conn.escape(args)
                
        result = 0
        try:
            result = self._query(query)
        except:
            exc, value, tb = exc_info()
            del tb
            self.messages.append((exc,value))
            self.errorhandler(self, exc, value)

        self._executed = query
        return result
    
    def executemany(self, query, args):
        ''' Run several data against one query '''
        del self.messages[:]
        conn = self._get_db()
        if not args:
            return
        charset = conn.charset
        if isinstance(query, unicode):
            query = query.encode(charset)
    
        self.rowcount = sum([ self.execute(query, arg) for arg in args ])
        return self.rowcount
    
    
    def callproc(self, procname, args=()):
        ''' Call a stored procedure. Take care to ensure that procname is
        properly escaped. '''
        if not isinstance(args, tuple):
            args = (args,)

        argstr = ("%s," * len(args))[:-1]

        return self.execute("CALL `%s`(%s)" % (procname, argstr), args)

    def fetchone(self):
        ''' Fetch the next row '''
        self._check_executed()        
        if self._rows is None or self.rownumber >= len(self._rows):
            return None
        result = self._rows[self.rownumber]
        self.rownumber += 1
        return result
    
    def fetchmany(self, size=None):
        ''' Fetch several rows '''
        self._check_executed()
        end = self.rownumber + (size or self.arraysize)
        result = self._rows[self.rownumber:end]
        if self._rows is None:
            return None
        self.rownumber = min(end, len(self._rows))
        return result

    def fetchall(self):
        ''' Fetch all the rows '''
        self._check_executed()
        if self._rows is None:
            return None
        if self.rownumber:
            result = self._rows[self.rownumber:]
        else:
            result = self._rows
        self.rownumber = len(self._rows)
        return result
    
    def scroll(self, value, mode='relative'):
        
        if mode == 'relative':
            r = self.rownumber + value
        elif mode == 'absolute':
            r = value
        else:
            self.errorhandler(self, ProgrammingError, 
                    "unknown scroll mode %s" % mode)

        if r < 0 or r >= len(self._rows):
            self.errorhandler(self, IndexError, "out of range")
        self.rownumber = r

    def _query(self, q):
        conn = self._get_db()
        self._last_executed = q
        conn.query(q)
        self._do_get_result()
        return self.rowcount
    
    def _do_get_result(self):
        conn = self._get_db()
        self.rowcount = conn._result.affected_rows
        
        self.rownumber = 0
        self.description = conn._result.description
        self.lastrowid = conn._result.insert_id
        self._rows = conn._result.rows
        self._has_next = conn._result.has_next
        conn._result = None
    
    def __iter__(self):
        self._check_executed()
        result = self.rownumber and self._rows[self.rownumber:] or self._rows
        return iter(result)
    
    Warning = Warning
    Error = Error
    InterfaceError = InterfaceError
    DatabaseError = DatabaseError
    DataError = DataError
    OperationalError = OperationalError
    IntegrityError = IntegrityError
    InternalError = InternalError
    ProgrammingError = ProgrammingError
    NotSupportedError = NotSupportedError
