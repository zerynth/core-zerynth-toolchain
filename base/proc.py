from .base import *
from .fs import *
from .cfg import *
import subprocess
import shlex

__all__=['proc']


class prc():
    def __init__(self):
        pass

    def init(self):
        #hack to avoid annoying windows consoles
        self.startupnfo = None
        if env.is_windows():
            self.startupnfo = subprocess.STARTUPINFO()
            self.startupnfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            self.startupnfo.wShowWindow = subprocess.SW_HIDE

        for d in fs.dirs(env.sys):
            try:
                bj = fs.get_json(fs.path(bdir,"device.json"))
                bj["path"] = bdir
                for cls in bj["class"]:
                    try:
                        sys.path.append(bdir)
                        module,bcls = cls.split(".")
                        bc = importlib.import_module(module)
                        dcls = getattr(bc,bcls)
                        bjc = dict(bj)
                        bjc["cls"]=dcls
                        sys.path.pop()
                        self.device_cls[bdir+"::"+bcls]=bjc
                    except Exception as e:
                        warning(e,err=True)
            except Exception as e:
                warning(e,err=True)


    def runcmd(self,cmd,*args):
        cmdval = env.get_command(cmd)
        if cmdval is None:
            return None #TODO: raise proper exception
        return self.run(cmdval,*args)

    def run(self,cmd,*args):
        try:
            if isinstance(cmd,str):
                cmd = cmd+" "+(" ".join(args))
            else:
                cmd.extend(args)
                cmd = " ".join(cmd)
            torun = shlex.split(cmd,posix=not env.is_windows())
            #TODO: consider swicth to Python 3.5 for subprocess.run
            res = subprocess.check_output(torun,universal_newlines=True,stderr=subprocess.STDOUT,startupinfo=self.startupnfo)
            #return res.returncode, res.stdout, res.stderr
            return 0,res,res
        except subprocess.CalledProcessError as e:
            return e.returncode,e.output,e.output


    def run_get_lines(self,cmd,*args):
        r,out,err = self.run(cmd,*args)
        for line in out.split("\n"):
            yield line



proc = prc()

add_init(proc.init)

