from .base import *
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

