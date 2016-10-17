from base import *

class ZpmException(Exception):
    
    def __init__(self,msg):
        super().__init__(self)
        self.msg=msg
    
    def __str__(self):
        return str(self.msg)

class ZpmVersion():
    
    def __init__(self,v=1):
        if isinstance(v,str):
            if not v.startswith("r"):
                raise ZpmException("Wrong version format!")
            self.v = v=v[1:]
            flds = v.split(".")
            self.x = (int(flds[0])<<32)|(int(flds[1])<<16)|(int(flds[2]))
            self.major = int(flds[0])
            self.minor = int(flds[1])
            self.patch = int(flds[2])
        elif isinstance(v,int):
            self.x = v
            self.major= (self.x>>32)&0xffff
            self.minor= (self.x>>16)&0xffff
            self.patch= self.x&0xffff
        self.head="r"

    def __str__(self):
        v="r"
        v+=str(self.major)+"."+str(self.minor)+"."+str(self.patch)
        return v
    
    def __int__(self):
        return self.x
    
    def __repr__(self):
        return str(self)
    
    def __gt__(self,v2):
        return self.x>v2.x
    
    def __ge__(self,v2):
        return self.x>=v2.x
    
    def __lt__(self,v2):
        return self.x<v2.x
    
    def __le__(self,v2):
        return self.x<=v2.x
    
    def __eq__(self,v2):
        return self.x==v2.x
    
    def __ne__(self,v2):
        return self.x!=v2.x
    
    def __bool__(self):
        return self.x!=0
    
    __nonzero__=__bool__
    
    def strhex_format(self):
        return str(format(int(self),'012X'))
    
    def max_compatible_version(self):
        if self.major:
            return ZpmVersion(((self.major)<<32)|(0xffff)|(0xffff))
        else:
            return ZpmVersion((self.minor<<16)|(0xffff))
    
    def pick_max_compatible_version(self,vlist):
        for z in reversed(vlist):
            if z.major==self.major:
                if z.major==0:
                    if z.minor==self.minor:
                        return z
                else:
                    return z
        return None

    def pick_min_compatible_version(self,vlist):
        for z in vlist:
            if z.major==self.major:
                if z.major==0:
                    if z.minor==self.minor:
                        return z
                else:
                    return z
        return None
