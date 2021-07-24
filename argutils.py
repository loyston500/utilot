import speedups

InitError = speedups.argutils.InitError
ArgNotFoundError = speedups.argutils.ArgNotFoundError
ValueNotFoundError = speedups.argutils.ValueNotFoundError

class MagicDict(dict):
    def __getattr__(self, attr):
        return self.get(attr)

class ArgParse:
    def __init__(self):
        self._arg_infos = []
        self._set_args = []
        
    def __getitem__(self, item):
        return self._set_args[item]

    def add_argument(self, names, id=None, default=None, greedy=True, optional=True):
        if id is None:
            id = names[-1].replace('-', '_')
            
        if not id.isidentifier():
            raise ValueError(f"{id} is not a valid identifier.")
        
        if id in dir(dict):
            raise ValueError(f"'{id}' clashes with dict's already existing atttribute.")
        
        self._arg_infos.append([names, id, default, greedy, optional])
        return self
        
    def test(self, test_list=[], strict=True):
        try:
            ret = speedups.argutils.argparse(test_list, self._arg_infos)
        except Exception as err:
            print(f"Argument Test {test_list} failed with exception {err.__class__.__name__}: {err}")
            if strict:
                raise err
        else:
            print(f"Argument Test {test_list} passed with result {ret}")
        return self
        
    def set_args(self, args):
        self._set_args = args
    
    def parse(self, args=None):
        if args is not None:
            kwargs, args = speedups.argutils.argparse(args, self._arg_infos)
        else:
            kwargs, args = speedups.argutils.argparse(self._set_args, self._arg_infos)
        
        return MagicDict(kwargs), args
    
    @staticmethod
    def wrap(argparse_obj):
        def factory(func):
            async def wrapper(snd, ctx, piped, args, **kwargs):
                argparse_obj.set_args(args)
                try:
                    return await func(snd, ctx, piped, argparse_obj, **kwargs)
                except ValueNotFoundError as err:
                    print(err.args)
                    snd.senderr(f"Option {', '.join(argparse_obj._arg_infos[err.args[0]][0])} requires an argument.")
                    snd.exitcode(1)
                except ArgNotFoundError as err:
                    print(err.args)
                    snd.senderr(f"Argument for {', '.join(argparse_obj._arg_infos[err.args[0]][0])} is mandatory.")
                    snd.exitcode(1)
            wrapper.__name__ = func.__name__
            wrapper.__doc__ = func.__doc__
            return wrapper
        return factory
            
