from base import *

import os
import ast
import struct
import base64
import hashlib
import tempfile
import glob
import shutil
import viper.toolbelt as toolbelt
import viper.viperconf as vconf

#toolbelt.viper_import("compiler.astwalker")
from compiler.astwalker import astdump, AstWalker
from compiler.astprep import AstPreprocessor
from compiler.utils.code import CodeRepr
from compiler.utils.env import Env
from compiler.utils.exceptions import *
from compiler.names import vipernames
from compiler.names import viperpinmap
from compiler import cc
from compiler import _board_family
import viper.viperlogger

logger = viper.viperlogger.logger(__name__,"compiler")


def get_filename(s):
    return os.path.split(s)[1]


#NO BOARD

class NoBoard():
    def __init__(self):
        self.board = "generic_board"
        self.pinmap = viperpinmap
        self.gcc = "arm"
        self.gccopts = {
            "cflags":["-mcpu=cortex-m3","-mthumb", "-O2","-fomit-frame-pointer","-falign-functions=16","-ffunction-sections", "-fdata-sections", "-fno-common", "-Wall", "-Wextra", "-Wstrict-prototypes","-nostdlib"],
            "defs":["GENERIC_BOARD"]
        }
        self.defines = {
            "BOARD":self.board,
            "LAYOUT": "arduino_uno"
        }
        self.names = vipernames.keys()
        self.family_name="stm32f4"


noboard = NoBoard()


class CNativeCache():
    def __init__(self):
        self.path = os.path.join(vconf.envdirs["tmp"],"native_cache")
        self.clear()

    def set_board(self,board,defs=[]):
        sdf=""
        for x in sorted(defs):
            sdf=sdf+str(x)+"&&"
        self.board=board+"::"+sdf
        #print("BOARD IS",self.board)
        

    def clear(self):
        shutil.rmtree(self.path,ignore_errors=True)
        os.makedirs(self.path,exist_ok=True)
        self.cache = {}
        self.board=""

    def add_object(self,cfile,ofile):
        hasher = hashlib.sha1()
        hasher.update(bytes(self.board,"utf-8"))
        hasher.update(bytes(cfile,"utf-8"))
        statinfo = os.stat(cfile)
        ofilename = os.path.split(ofile)[1]
        cdirname = os.path.join(self.path,hasher.hexdigest())
        self.cache[self.board+cfile]=[statinfo.st_mtime,os.path.join(cdirname,ofilename)]
        os.makedirs(cdirname,exist_ok=True)
        shutil.copyfile(ofile,os.path.join(cdirname,ofilename))
        #print("CACHE added",cfile,"=>",self.cache[cfile])

    def has_object(self,cfile):
        hfile = self.board+cfile
        if hfile in self.cache:
            statinfo = os.stat(cfile)
            #print(cfile,"=>",self.cache[cfile],"==",statinfo.st_mtime)
            if statinfo.st_mtime!=self.cache[hfile][0]:
                #file has been changed
                return False
            else:
                return self.cache[hfile][1]
        return False

cncache = CNativeCache()
libdir = os.path.abspath(os.path.dirname(__file__))

class Compiler():

    def __init__(self, inputfile, board=noboard,logfn=None,syspath=[],prvmods={}):
        #curdir =os.path.abspath(os.path.dirname(__file__))
        self.syspath = []
        self.syspath.extend(syspath)
        self.syspath.append(os.path.split(os.path.abspath(inputfile))[0])
        self.prvmods = prvmods
        self.mainfile = inputfile
        self.logfn=logfn
        self.phase = 0
        self.env = Env()
        self.vmsym = []
        self.board = board
        self.parseNatives();
        self.builtins_module = "__builtins__"
        if board.names:
            bnames = {k:v for k,v in vipernames.items() if k in board.names}
        else:
            bnames = vipernames
        if board.pinmap:
            bpinmap = board.pinmap
        else:
            bpinmap = viperpinmap
        self.prepcfiles = set()
        self.prepdefines = {}
        self.prepdefines.update(board.defines)
        self.astp = AstPreprocessor(bnames,bpinmap,self.prepdefines,self.prepcfiles)
        self.scopes = {}
        self.moduletable = {}
        self.maindir=None
        self.resources={}
        self.families = _board_family.get_families
        self.cncache = cncache
        self.scratch()

    def scratch(self):
        self.codeobjs = []
        self.codemap = {}
        self.modules = {}
        self.cnatives = {}
        self.cdefines = set()
        self.cincpaths = set()
        self.cfiles = set()
        self.reachable_names = set()   
        self.reachable_modules = set()     
        self.bltinfo = {}
        self.stripped_modules = set()
        self.stripped = set()
        self.maindir=None
        self.resources={}
        
        
    def log(self,msg):
        if self.logfn:
            self.logfn(msg)

    def newPhase(self):    
        self.codeobjs = []
        self.modules = {}
        self.bltinfo = {}
        self.stripped = set()
        self.lastbuiltincode = 1


    def shouldGenerateCodeFor(self,name,module):
        return True
        # if self.phase == 0:
        #     return True
        # fullname = module+"."+name
        # return fullname in self.reachable_names

    def shouldGenerateModule(self,name):
        if self.phase <= 2:
            return True
        return name not in self.stripped_modules


    def getBuiltinCoding(self,name):
        # nfo = self.bltinfo[name]
        # # code(8)|vararg(1)|kwargs(3)|args(4)
        # return (nfo[0]<<8)|((nfo[1][2]<<7)|(nfo[1][1]<<4)|(nfo[1][0]))
        bltmod = self.modules[self.builtins_module]
        #print(bltmod.scope.locals)
        return bltmod.scope.locals.index(name)

    def saveBuiltinInfo(self,name,code,args):
        self.bltinfo[name] = (code,args)
        self.lastbuiltincode = code

    def saveBuiltinNameInfo(self,name):
        self.lastbuiltincode+=1
        self.bltinfo[name] = (self.lastbuiltincode,(0,0,0))

    def putModuleCode(self,name,code):
        self.modules[name]=code

    def getModuleCode(self,name):
        return self.modules[name]

    def pushCodeHook(self, code):
        self.codeobjs.append(code)

    def getEnvHook(self):
        #tenv = self.env
        self.env = Env()
        #self.env.transferHyperGlobals(tenv)
        return self.env

    def numCodeHook(self):
        return len(self.codeobjs)

    def importHook(self,name,line,filename):
        logger.info("   Importing module: %s",name)
        self.compileModule(name,line,filename)

    def addResource(self,filename):
        if os.path.exists(os.path.join(self.maindir,filename)):
            ret = len(self.resources)
            self.resources[filename]=ret
            return ret
        return -1


    def addCThings(self,natives,files,vbls,opts,fbase=""):
        #print("addCThings:",natives,files,vbls,opts,fbase)
        for file in files:
            file.replace("/",os.path.sep);
            if file.endswith("*"):
                pt = os.path.split(file)[0]
                #print("!!!",glob.glob(os.path.join(pt,"*.c")))
                afile = [ x.replace("\\","/") for x in glob.glob(os.path.join(pt,"*.c"))]
            else:
                afile = [file.replace("\\","/")]
            self.cfiles.update(afile)
        for vbl in vbls:
            if vbl.startswith("VBL_"):
                vblf = os.path.join(vconf.envdirs["vm"],"common","vbl",vbl.lower()+".c")
                if os.path.exists(vblf):
                    self.cfiles.add(vblf)
                    self.cincpaths.add(os.path.realpath(os.path.join(vconf.envdirs["vm"],"common","vbl")))
                else:
                    raise CNativeNotFound(0,0,vblf)
            elif vbl.startswith("VHAL_"):
                self.cdefines.add(vbl)
                lookup = self.families()[self.board.family_name]
                if vbl in lookup["vhal"]:
                    for x in lookup["vhal"][vbl]["src"]:
                        self.cfiles.add(os.path.realpath(os.path.join(vconf.envdirs["vhal"],lookup["path"],x)))
                    for x in lookup["vhal"][vbl]["inc"]:
                        self.cincpaths.add(os.path.realpath(os.path.join(vconf.envdirs["vhal"],lookup["path"],x)))
                    self.cdefines.update(lookup["vhal"][vbl]["defs"])
            else:
                self.cdefines.add(vbl)
        for opt in opts:
            if opt.startswith("-I"):
                self.cincpaths.add(os.path.realpath(opt[2:].replace("...",fbase)))
        if isinstance(natives,str):
            if natives not in self.cnatives:
                self.cnatives[natives]=len(self.cnatives)
        else:
            for x in natives:
                if x not in self.cnatives:
                    self.cnatives[x]=len(self.cnatives)

    def decodeCNative(self,cnative):
        #print("decodeCNative:",cnative,self.cnatives)
        if cnative in self.cnatives:
            return self.cnatives[cnative]
        else:
            return -1

    def searchModule(self,name):
        mfile = None
        cdir = os.path.dirname(__file__)
        nm = name.replace(".",os.sep);
        #search syspath
        for k in self.syspath:
            mdir = k if os.path.isabs(k) else os.path.join(cdir,k)
            mfile = os.path.join(mdir,nm+".py")
            logger.info("   Searching in %s",mfile)
            if os.path.isfile(mfile):
                logger.info(" ok")
                break
            else:
                mfile=None
                logger.info(" not found!")
        else:
            #search private modules
            print("Searching private modules",self.prvmods)
            for k,v in self.prvmods.items():
                if name.startswith(k):
                    nm=name.replace(k,"").replace(".",os.sep).strip(os.sep)
                    mfile = os.path.join(v,nm+".py")
                    logger.info("   #Searching in %s %s %s",mfile,k,v)
                    if os.path.isfile(mfile):
                        logger.info(" ok")
                        break
                    else:
                        mfile=None
                        logger.info(" not found!")
        return mfile

    def find_imports(self):
        ## Preload builtins to get all __defines
        astp = AstPreprocessor({},{},self.prepdefines,self.prepcfiles,just_imports=True)
        with open(self.mainfile) as ff:
            modprg = ff.read()
        tree = ast.parse(modprg)
        astp.visit(tree)
        res = {}
        ures = set()
        for modname in astp.modules:
            flp = self.searchModule(modname)
            if not flp:
                ures.add(modname)
            else:
                res[flp]=modname
        return (res,ures)

    def compileModule(self,name,line=0,filename=0):
        logger.info("Compiling module [%s]",name)
        #print(self.env)
        if ".py" in name:
            mfile = name
            name = "__main__"
            self.maindir = os.path.split(mfile)[0]
        else:
            mfile = self.searchModule(name)
        
        self.log("[COMPILER]: Compiling module [%s]"% name)
        
        if mfile!=None:
            f= open(mfile)
            modprg = f.read()
            f.close()
            if name!=self.builtins_module:
                modprg = "import "+self.builtins_module+"\n"+modprg
            try:
                tree = ast.parse(modprg)
            except SyntaxError as e:
                self.log("[COMPILER]: Oooops, Syntax error in file %s"%mfile)
                raise CSyntaxError(e.lineno,e.offset,mfile)
            self.astp.curpath = os.path.split(mfile)[0]
            tree = self.astp.visit(tree)
            if self.phase==0 and name!="__builtins__":
                #print("\n\n## Syntax Tree ##\n")
                #print(astdump(tree))
                pass

            #astf = AstFiller(self.env,mfile,name)
            self.astp.clean(tree)
            #astf.visit(tree)
            #print("allnames==>>>",self.astp.allnames)
            #print(astdump(tree))
            
            #print("BEFORE compiling:",name)
            #self.env.print_scopedir()
            #scopedir = self.env.get_scopedir()
            
            mc = AstWalker(modprg,self,mfile,name,None if self.phase==0 else self.scopes)
            mc.visit(tree)
            self.scopes.update(mc.env.get_scopedir())
            self.moduletable[mfile]=name

        else:
            raise CModuleNotFound(line,0,filename,name)

    def compile(self):
        self.log("[COMPILER]: Compiling ZERYNTH code for "+self.board.board)
        ## Preload builtins to get all __defines
        mf = self.searchModule(self.builtins_module)
        with open(mf) as ff:
            modprg = ff.read()
        tree = ast.parse(modprg)
        self.astp.visit(tree)

        #Phase 0: compile everything
        logger.info("PHASE 1: first pass compile")
        #self.log("####### First pass compile")
        self.phase = 0
        self.newPhase()
        self.compileModule(self.mainfile)
        objs_at_0 = len(self.codeobjs)
        mods_at_0 = len(self.modules)
        

        # print("SCOPEDIR")
        # for k in sorted(self.scopes):
        #     print(k,"==>",self.scopes[k]["scope"])
        
        self.scratch()
        #Phase 0: compile everything
        logger.info("PHASE 2: second pass compile")
        #self.log("####### First pass compile")
        self.phase = 1
        self.newPhase()
        self.compileModule(self.mainfile)
        objs_at_0 = len(self.codeobjs)
        mods_at_0 = len(self.modules)




        #print(self.bltinfo)

        # #Phase 1: compute reachable code
        # logger.info("PHASE 2: compute reachability (not implemented yet)")
        # self.phase = 1
        # #self.computeReachableCode()


        # #Phase 2: compile stripped code
        # logger.info("PHASE 3: second pass compile")
        # self.phase = 2
        # self.newPhase()
        # self.compileModule(self.mainfile)
        # objs_at_2 = len(self.codeobjs)
        
        # for k,v in self.modules.items():
        #     if v.isJustStop():
        #         self.stripped_modules.add(k);

        # mods_at_2 = len(self.modules)

        # #print("\n   Stripped codeobjs:",objs_at_0-objs_at_2)
        # #print("   Stripped modules:",mods_at_0-mods_at_2)

        # #Phase 4: strip modules
        # logger.info("PHASE 4: third pass compile")
        # self.phase = 3
        # self.newPhase()
        # self.compileModule(self.mainfile)
        # mods_at_3 = len(self.modules)
        # objs_at_3 = len(self.codeobjs)

        # #print("\n   Stripped codeobjs:",objs_at_0-objs_at_3)
        # #print("   Stripped modules:",mods_at_0-mods_at_3)

        self.cfiles.update(self.prepcfiles)
        if self.cfiles:
            logger.info("PHASE 5: compile native code")
            self.log("[COMPILER]: Compiling C code...")
            #print(self.cfiles);
            #tmpdir = tempfile.mkdtemp(prefix="cmp_")
            gccopts = dict(self.board.gccopts)
            if "CDEFS" in self.prepdefines:
                self.cdefines.update(self.prepdefines["CDEFS"])
            
            gccopts["defs"].extend(self.cdefines)
            
            bf = toolbelt.get_board_info(self.board.board)
            gccopts["inc"]=set(self.cincpaths)
            gccopts["inc"].add(os.path.realpath(os.path.join(vconf.envdirs["core"],"compiler","cdefs")))
            gccopts["inc"].add(os.path.realpath(os.path.join(vconf.envdirs["core"],"vm","lang")))
            gccopts["inc"].add(os.path.realpath(os.path.join(vconf.envdirs["core"],"vm","common","inc")))
            gccopts["inc"].add(os.path.realpath(os.path.join(vconf.envdirs["core"],"vm","common","inc")))
            gccopts["inc"].add(os.path.realpath(os.path.join(bf["path"],"port")))
            gccopts["inc"].add(os.path.realpath(os.path.join(bf["path"],"port","config")))
            
            gcc = cc.gcc(toolbelt.tools[self.board.cc],gccopts,logger=logger)
            ofilecnt = None
            self.cncache.set_board(self.board.board,self.cdefines)
            with tempfile.TemporaryDirectory(prefix="cmp_",dir=vconf.envdirs["tmp"]) as tmpdir:
                for cfile in self.cfiles:
                    if not os.path.exists(cfile):
                        self.log("[COMPILER]: %s does not exists!" %cfile)

                    if cfile.endswith(".rvo"):
                        #handle rvo files
                        self.log("[COMPILER]: Including precompiled binary %s"%cfile)
                        shutil.copyfile(cfile,os.path.join(tmpdir,get_filename(cfile).replace(".rvo",".o")))
                    else:
                        #handle c files
                        cnr = self.cncache.has_object(cfile)
                        if cnr:
                            logger.info("Getting: %s from cache",cfile)
                            self.log("[COMPILER]: Getting: %s from cache"%cfile)
                            shutil.copyfile(cnr,os.path.join(tmpdir,get_filename(cfile).replace(".c",".o")))
                        else:
                            logger.info("Compiling: %s",cfile)
                            self.log("[COMPILER]: Compiling: %s" %cfile)
                            outfile = os.path.join(tmpdir,get_filename(cfile).replace(".c",".o"))
                            ret,wrn,err,cout = gcc.compile([cfile],odir=tmpdir)
                            if ret==0:
                                if wrn:
                                    logger.info("WARNINGS: %i",len(wrn))
                                    for k,v in wrn.items():
                                        for vv in v:
                                            logger.info("%s => line %i: %s",k,vv[0],vv[2])
                                self.cncache.add_object(cfile,outfile)
                            else:
                                logger.info("ERRORS: %i",len(err))
                                for k,v in err.items():
                                    for vv in v:
                                        logger.info("%s => line %i: %s",k,vv[0],vv[2])
                                efl,evl = err.popitem()
                                self.log("[COMPILER]: Oooops, errors in C code")
                                self.log("[COMPILER]: "+str(evl[0][0])+":"+str(evl[0][1])+":"+str(evl[0][2]))
                                raise CNativeError(evl[0][0],evl[0][1],efl,evl[0][2])
                logger.info("Compile stage successful, now it's linking time...")
                self.log("[COMPILER]: Linking C code...")
                obcfile = os.path.join(tmpdir,"zerynth.vco") 
                ofile = os.path.join(tmpdir,"zerynth.rlo")
                #ofiles = [os.path.join(tmpdir,get_filename(c).replace(".c",".o")) for c in self.cfiles if "vhal_" not in get_filename(c) and get_filename(c).endswith(".c")]
                obcfiles = [os.path.join(tmpdir,get_filename(c).replace(".c",".o")) for c in self.cfiles if not get_filename(c).startswith("vhal_") and get_filename(c).endswith(".c")]
                vhalfiles = [os.path.join(tmpdir,get_filename(c).replace(".c",".o")) for c in self.cfiles if get_filename(c).startswith("vhal_") and get_filename(c).endswith(".c")]
                rvofiles = [os.path.join(tmpdir,get_filename(c).replace(".rvo",".o")) for c in self.cfiles if not get_filename(c).startswith("vhal_") and get_filename(c).endswith(".rvo")]
                
                #print(obcfiles,vhalfiles,rvofiles)
                # linking non vhal, non rvo
                if obcfiles:
                    ret,output = gcc.link(obcfiles,{},reloc=True,ofile=obcfile)
                    if ret!=0:
                        logger.error("Linking Time Error: %s",output);
                        self.log("[COMPILER]: Oooops, errors while linking! %s"%(str(output)))
                        raise CNativeError(0,0,"","C Native Linking Error!")
                    #save relocatable viper object
                    shutil.copy(obcfile,os.path.join(vconf.envdirs["tmp"],"lastbuilt.rvo"))

                ofiles = []
                ofiles.extend(obcfiles)
                ofiles.extend(vhalfiles)
                ofiles.extend(rvofiles)
                ret,output = gcc.link(ofiles,{},reloc=True,ofile=ofile)
                if ret!=0:
                    logger.error("Linking Time Error: %s",output);
                    self.log("[COMPILER]: Oooops, errors while linking! %s"%(str(output)))
                    raise CNativeError(0,0,"","C Native Linking Error!")
                logger.error("Linking Time: %s",output);
                sym = gcc.symbol_table(ofile)
                sym.info()
                syms = sym.symbols()
                logger.info("Linked symbols:")
                for ss in syms:
                    logger.info("==> %s",ss)
                logger.info("Undefined symbols:")
                undf = sym.getfrom(sym.undef)
                undf = {k:v for k,v in undf.items() if k not in set(self.vmsym)}
                for uu in undf:
                    logger.info("==> %s",uu)
                csym = frozenset(self.cnatives)
                if not( csym<=syms):
                    self.log("[COMPILER]: Oooops, some natives are not defined! %s"%(str(csym-syms)))
                    raise CNativeError(0,0,"","some C natives are not defined!!")
                with open(ofile,"rb") as ofilef:
                    ofilecnt = ofilef.read()
                if len(undf)>0:
                    self.log("[COMPILER]: Oooops, there are undefined symbols! %s"%(str(undf)))
                    logger.error("There are undefined symbols! %s",str(undf))
                    raise CNativeError(0,0,"","undefined symbols!")
        else:
            ofilecnt = bytearray()
            if self.cnatives:
                self.log("[COMPILER]: Oooops, some natives are not defined! %s"%(str(self.cnatives)))
                raise CNativeError(0,0,"","some C natives are not defined!!")

        #Phase 4: generate binary repr and debug file
        logger.info("PHASE 6: generate binary")
        self.phase = 4

        rt = self.generateBinary(ofilecnt)

        
        self.log("[COMPILER]: Everything Done!")
        return rt


    def generateResourceTable(self):
        head = bytearray()
        res = bytearray()
        headsize=0
        for name in self.resources:
            headsize+=4+4+4+len(os.path.split(name)[1])
            if headsize%4!=0:
                headsize+=4-headsize%4

        if headsize:
            head+=struct.pack("=I",headsize+4)
            headsize+=4

        for name in self.resources:
            with open(os.path.join(self.maindir,name),"rb") as rf:
                bin = rf.read()
            rname = os.path.split(name)[1]
            head+=struct.pack("=I",len(rname))
            head+=struct.pack("=I",len(bin))
            head+=struct.pack("=I",headsize+len(res))
            head+=struct.pack("="+str(len(rname))+"s", rname.encode("latin1"))
            #pad head
            if len(rname)%4!=0:
                for x in range(4-len(rname)%4):
                    head+=struct.pack("=B",0)
            res+=bin
        #pad res
        if len(res)%4!=0:
            for x in range(4-len(res)%4):
                res+=struct.pack("=B",0)
        return head+res

    def generateBinary(self,ofile=None):
        bin = {}
        self.env.buildExceptionTable()
        codereprs = []
        for co in self.codeobjs:
            co.resolveExceptions(self.env)
            #if co.module!="__builtins__":
            #print(str(co))
            cr = CodeRepr()
            cr.makeFromCode(co)
            #codereprs.append(cr.toIndex())
            codereprs.append(cr)


        # Generate Code Image
        objbuf = []        
        buf = bytearray()
        for co in self.codeobjs:
            bcf = co.toBytes()
            objbuf.append(bcf)

        #Generate Header
        #Magic Number
        buf+= (struct.pack("=B", ord('G') )) #GGGD
        buf+= (struct.pack("=B", ord('G') )) #GGGD
        buf+= (struct.pack("=B", ord('G') )) #GGGD
        buf+= (struct.pack("=B", ord('D') )) #GGGD
        #Flags
        buf+= (struct.pack("=B", 0 ))
        #NModules
        buf+= (struct.pack("=B", len(self.modules) ))
        #Nobjs
        buf+= (struct.pack("=H", len(objbuf) ))
        
        #Exceptions
        etable,emtable,emtablelen = self.env.getBinaryExceptionTable()
        rtable = self.generateResourceTable()
        buf+=struct.pack("=H",len(etable))
        #Unused --> now is num of cnatives
        buf+=struct.pack("=H",len(self.cnatives))
        #ram_start
        buf+=struct.pack("=I",0)
        #data_start
        buf+=struct.pack("=I",0)
        #data_end
        buf+=struct.pack("=I",0)
        #data_bss
        buf+=struct.pack("=I",0)


        cobsz = 4*len(objbuf)+(len(buf)+4)+(len(etable)*8+emtablelen)+4*len(self.cnatives)
        
        #res_table
        if rtable:
            buf+=struct.pack("=I",cobsz)
            cobsz+=len(rtable)
        else:
            buf+=struct.pack("=I",0)


        #CodeObjs table
        cobsztable = []
        pyobjtablestart = len(buf)
        #print("CodeObjTable starts at",len(buf),"pointing at",cobsz)
        for cob in objbuf:
            buf+=(struct.pack("=I", cobsz ))
            cobsztable.append(cobsz)
            #print("CodeObj Table",cobsz)
            cobsz+=len(cob)
        pyobjtableend = len(buf)
        
        #add space for c natives addrs
        for i in range(0,len(self.cnatives)):
            buf+=(struct.pack("=I", i ))

        etablestart = len(buf)
        #print("CodeObjTable ends at",len(buf))
        #exception table
        for e in etable:
            buf+=struct.pack("=H",e[0]) #name
            buf+=struct.pack("=H",e[1]) #parent
            buf+=struct.pack("=I",e[2]) #msg offs
            #print("etable entry:",e[0],e[1],e[2])

        pckd=0
        for e in emtable:
            buf+=struct.pack("=H",e[0]) #len
            buf+=struct.pack("="+str(e[0])+"s", e[1].encode("latin1")) #str
            pckd+=2+e[0]
            ssz = (len(buf))%4
            #print("etable entry:",e[0],e[1])
            if ssz:
                ssz=4-ssz
                while ssz>0:
                    buf+=struct.pack("=B",0) #pad
                    pckd+=1
                    ssz-=1
        #print("ExceptionTable ends at",len(buf),"pckd",pckd,"mlen",emtablelen)
        etableend = len(buf)
        #print(etable)
        
        #resource table
        buf+=rtable

        bin["info"]={
            "nmodules":len(self.modules),
            "npyobjs":len(objbuf),
            "pyobjtable_start":pyobjtablestart,
            "pyobjtable_end":pyobjtableend,
            "ncnatives":len(self.cnatives),
            "etable_start":etablestart,
            "etable_end":etableend,
            "rtable_start":etableend,
            "rtable_elements": len(self.resources),
            "header_size": len(buf),
            "version":vconf.get_full_viper_version(),
            "board":self.board.board,
            "baud":self.board.baud
        }

        bin["header"]=str(base64.standard_b64encode(buf),'utf-8')
        buf = bytearray()


        #Store CodeObjs
        for ic,cob in enumerate(objbuf):
            #print("CodeObject",ic,"[",self.codeobjs[ic].fullname,"]","starts at",len(buf),"with nmstart",self.codeobjs[ic].nmstart,"and bcstart",self.codeobjs[ic].bcstart)
            buf+=cob

        bin["pyobjs"]=str(base64.standard_b64encode(buf),'utf-8')
        bin["info"]["pyobjs_size"]=len(buf)
        bin["cobjs"]=None
        bin["modules"]=self.moduletable

        onatives = {v:k for k,v in self.cnatives.items()}
        bin["cnatives"]=[onatives[i] for i in range(0,len(onatives))]
        if ofile:
            bin["cobjs"]=str(base64.standard_b64encode(ofile),'utf-8')

        #print("\n","#"*80,sep="")
        #print("Code Size:",0,"bytes");
        #print("Code Objs:",len(objbuf))
        #for i,cob in enumerate(objbuf):
        #    print("         - Obj",i,"is",str(len(cob)),"bytes","[",self.codeobjs[i].fullname,"] @",cobsztable[i])
        #print("\n","#"*80,sep="")
        
        bin["stats"]={}
        homepath = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)),".."))
        bin["stats"]["modules"]={k.replace(homepath,""):v for k,v in self.moduletable.items() }
        bin["stats"]["natives"]=self.cnatives
        bin["stats"]["cfiles"]=[os.path.abspath(k).replace(homepath,"") for k in self.cfiles]
        bin["stats"]["board"]=self.board.board
        #print(bin)
        return (bin,codereprs, self.codeobjs)


    def parseNatives(self):
        import re
        fname = os.path.join(vconf.envdirs["vm"],"lang","natives.def")
        with open(fname) as f:
            lines = f.readlines()
            for txt in lines:
                #print(txt)
                m = re.search('BUILD_NATIVE\(([a-zA-Z0-9_ \t]*),',txt)
                if m and m.group(1):
                    #print("Adding Native:",m.group(1))
                    self.env.addNative(m.group(1).strip())
        fname = os.path.join(vconf.envdirs["vm"],"lang","pnames.h")
        with open(fname) as f:
            lines = f.readlines()
            for txt in lines:
                m = re.search(' NAME_([a-zA-Z0-9_]*)',txt)
                #print(txt)
                if m and m.group(1):
                    #print("Adding Name:",m.group(1).lower())
                    self.env.addNameCode(m.group(1))
        if self.board!=noboard:
            fname = os.path.join(toolbelt.get_board_info(self.board.board)["path"],"port","config","vmsym.def")
            with open(fname) as f:
                lines = f.readlines()
                for txt in lines:
                    m = re.match('\s*(SYM|VAR)\((.*)\)',txt)
                    if m and m.group(2):
                        self.vmsym.append(m.group(2))




