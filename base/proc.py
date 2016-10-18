from .base import *
from .cfg import *
from .tools import *
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

    def runcmd(self,cmd,*args,outfn=None):
        cmdval = tools[cmd]
        if cmdval is None:
            return 1,"","" #TODO: raise proper exception
        return self.run(cmdval,*args,outfn=outfn)

    def run(self,cmd,*args,outfn=None):
        try:
            if isinstance(cmd,str):
                cmd = cmd+" "+(" ".join(args))
            else:
                cmd.extend(args)
                cmd = " ".join(cmd)
            torun = shlex.split(cmd,posix=not env.is_windows())
            #TODO: consider swicth to Python 3.5 for subprocess.run
            p=subprocess.Popen(torun,universal_newlines=True,stderr=subprocess.STDOUT,startupinfo=self.startupnfo,stdout=subprocess.PIPE)
            lines=[]
            for line in p.stdout:
                lines.append(line)
                if outfn: outfn(line.strip("\n"))
            p.wait()
            #res = subprocess.check_output(torun,universal_newlines=True,stderr=subprocess.STDOUT,startupinfo=self.startupnfo)
            #return res.returncode, res.stdout, res.stderr
            res = "".join(lines)
            return p.returncode,res,res
        except subprocess.CalledProcessError as e:
            return e.returncode,e.output,e.output


    def run_get_lines(self,cmd,*args):
        r,out,err = self.run(cmd,*args)
        for line in out.split("\n"):
            yield line



proc = prc()

add_init(proc.init)

