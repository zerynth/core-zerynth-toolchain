
__all__=["CError","CSyntaxError", "CNameError","CNameConstantError", "CUnsupportedFeatureError","CWrongSyntax","CUnknownNative","CNativeError","CModuleNotFound"]

class CError(Exception):
    def __init__(self,line,col,filename):
        self.line = line
        self.col = col;
        self.filename = filename
        self.errmsg = ""
        self.errtype ="Error"
    def toCleanStr(self):
        return self.errtype+": "+self.errmsg
    def __str__(self):
        return self.errtype+" @<"+str(self.filename)+">:"+str(self.line)+","+str(self.col)+": "+self.errmsg


class CModuleNotFound(CError):
    def __init__(self,line,col,filename,module=""):
        super().__init__(line,col,filename)
        self.errmsg = "Module not found!"
        self.module=module

class CNativeNotFound(CError):
    def __init__(self,line,col,filename):
        super().__init__(line,col,filename)
        self.errmsg = "File not found! "+str(filename)


class CSyntaxError(CError):
    def __init__(self,line,col,filename):
        super().__init__(line,col,filename)
        self.errmsg = ""
        self.errtype = "SyntaxError"

class CNameError(CSyntaxError):
    def __init__(self,line,col,filename,name):
        super().__init__(line,col,filename)
        self.errmsg="Unknown name -> "+str(name)

class CNameConstantError(CSyntaxError):
    def __init__(self,line,col,filename):
        super().__init__(line,col,filename)
        self.errmsg="Unknown Constant"

class CUnsupportedFeatureError(CSyntaxError):
    def __init__(self,line,col,filename, feature):
        super().__init__(line,col,filename)        
        self.errmsg="Unsupported Feature -> "+str(feature)    

class CWrongSyntax(CSyntaxError):
    def __init__(self,line,col,filename,msg):
        super().__init__(line,col,filename)
        self.errmsg=msg

class CUnknownNative(CError):
    def __init__(self,line,col,filename,msg):
        super().__init__(line,col,filename)
        self.errmsg="Unknown C Native -> "+str(msg)

class CNativeError(CError):
    def __init__(self,line,col,filename,msg):
        super().__init__(line,col,filename)
        self.errmsg = msg
        self.errtype = "C Native Error"