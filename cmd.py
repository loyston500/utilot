import inspect
import yaml

class Snd:
    def __init__(self, out=None, err=None, stuff=None, exception=None, exitcode=0):
        self._out = [] if out is None else out 
        self._err = [] if err is None else err 
        self._stuff = [] if out is None else out 
        self._exception = exception
        self._exitcode = exitcode
        
    def sendout(self, byts, end=b'\n'):
        if type(byts) == str:
            byts = byts.encode()
        self._out.append(byts + end)
        
    def senderr(self, byts, end=b'\n'):
        if type(byts) == str:
            byts = byts.encode()
        self._err.append(byts + end)
        
    def sendstuff(self, stuff):
        self._stuff.append(stuff)
        
    def sendexception(self, exception):
        self._exception = exception
        
    def exitcode(self, code):
        self._exitcode = code
        
        
class Cmd:
    def __init__(self):
        self._commands = {}
    
    def get(self, name):
        return self._commands[name]
            
    @staticmethod
    def is_async(func):
        return inspect.iscoroutinefunction(func)
    
    def on_exception(self, exception, to_do):
        def factory(func):
            async def wrap(*args, **kwargs):
                try:
                    return await func(*args, **kwargs)
                except exception as err:
                    to_do(*args, **kwargs)
            wrap.__name__ = func.__name__
            wrap.__doc__ = func.__doc__
            return wrap
        return factory
                    
            
    
    def new(self, name=None, aliases=[]):
        def factory(func):
            if inspect.iscoroutinefunction(func):
                async def wrap(*args, **kwargs):
                    snd = Snd()
                    try:
                        await func(snd, *args, **kwargs)
                    except NotImplementedError as err:
                        snd.senderr('this feature is not implemented')
                        snd.exitcode(2)

                    return snd
            else:
                raise Exception(f"{func} not a coroutine")
            
            if name:
                wrap.__name__ = name
            else:
                wrap.__name__ = func.__name__
            
            if func.__doc__:
                try:
                    doc = func.__doc__.format(
                        name=func.__name__,
                        al=aliases,
                    )
                    doc = yaml.safe_load(doc)
                except Exception as err:
                    raise Exception(f"command {wrap.__name__}: {err}")
                else:
                    wrap.__doc__ = doc
            
            self._commands[wrap.__name__] = wrap
            print("Added", wrap.__name__)
            
            return wrap
        
        return factory
    
    def has(self, name):
        return name in self._commands

cmd = Cmd()
