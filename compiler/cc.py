from base import *
import re


# CPU = -mcpu=cortex-m4 -mthumb -mfpu=fpv4-sp-d16 -mfloat-abi=$(FLOAT_ABI)
# CC_FLAGS = $(CPU) -c -g -fno-common -fmessage-length=0 -Wall -fno-exceptions -ffunction-sections -fdata-sections -fomit-frame-pointer -fdiagnostics-color=auto
# CC_FLAGS += -MMD -MP


# -mcpu=cortex-m4 -O2 -ggdb -fomit-frame-pointer -falign-functions=16 -fdiagnostics-color=auto -ffunction-sections -fdata-sections -fno-common  -Wall -Wextra -Wstrict-prototypes
# -MD -MP -MF
# -mthumb


class ZerynthCObj():
    def __init__(self):
        self.sections = {}
        self.binary = bytearray()
        self.data = [None,None,None]
        self.rodata = [None,None,None]
        self.text = [None,None,None]
        self.bss = [None,None,None]
        self.romdata = [None,None,None]
        self.symbols = {}        
    def add_data(self, section, data):
        if section:
            if section not in self.sections:
                self.sections[section]=bytearray()
            self.sections[section].append(data)
    def finalize(self,table):
        #print("Finalizing with",table.table)
        has_bss = ".bss" in table.sections
        has_data = ".data" in table.sections
        has_rodata = ".rodata" in table.sections
        has_text = ".text" in table.sections
        #print(has_bss,has_data,has_rodata,has_text)
        #print(table)
        #table.info()
        for k,v in table.table.items():
            #print("Checking",k,v)
            if v[3]==".text":
                self.symbols[v[0]]=int(v[2],16)
            elif v[3]==".bss" and (v[0]=="__bss_end__" or v[0]=="_end"):
                bss_end = int(v[2],16)
            elif v[3]==".data" and v[0]=="_edata":
                data_end = int(v[2],16)
        if has_bss:            
            bss_start = int(table.sections[".bss"][2],16)
            self.bss = [bss_start,bss_end,bss_end-bss_start]
        if has_text:
            text_start = int(table.sections[".text"][2],16)
            text_end = text_start+len(self.sections[".text"])
            self.text = [text_start,text_end,text_end-text_start]
            #print("extending .text",len(self.binary))
            self.binary.extend(self.sections[".text"])
            #print("extended .text",len(self.binary))
        if has_rodata:
            rodata_start = int(table.sections[".rodata"][2],16)
            rodata_end = int(rodata_start)+len(self.sections[".rodata"])
            self.rodata = [rodata_start,rodata_end,rodata_end-rodata_start]
            #print("extending .rodata",len(self.binary))
            self.binary.extend(self.sections[".rodata"])        
            #print("extended .rodata",len(self.binary))
        if has_data:
            data_start = int(table.sections[".data"][2],16)
            self.data = [data_start,data_end,data_end-data_start]            
            if has_rodata:
                data_rom_start = rodata_end
                data_rom_end = data_rom_start+len(self.sections[".data"])    
                self.romdata = [data_rom_start,data_rom_end,data_rom_end-data_rom_start]
            elif has_text:
                data_rom_start = text_end
                data_rom_end = data_rom_start+len(self.sections[".data"])    
                self.romdata = [data_rom_start,data_rom_end,data_rom_end-data_rom_start]
            else:
                pass                
                #RAISE EXCEPTION! no cobj without .text allowed
            #print("extending .romdata",len(self.binary))
            self.binary.extend(self.sections[".data"])
            #print("extended .romdata",len(self.binary))
                
    def info(self):
        if self.data[0]:
            print(".data   :",hex(self.data[0]),"=>",hex(self.data[1]),"::",hex(self.data[2]))
        if self.bss[0]:
            print(".bss    :",hex(self.bss[0]),"=>",hex(self.bss[1]),"::",hex(self.bss[2]))
        if self.text[0]:
            print(".text   :",hex(self.text[0]),"=>",hex(self.text[1]),"::",hex(self.text[2]))
        if self.rodata[0]:
            print(".rodata :",hex(self.rodata[0]),"=>",hex(self.rodata[1]),"::",hex(self.rodata[2]))
        if self.romdata[0]:
            print(".romdata:",hex(self.romdata[0]),"=>",hex(self.romdata[1]),"::",hex(self.romdata[2]))
        print("binsize :",len(self.binary))
        for sym,addr in self.symbols.items():
            print(hex(addr),"::",sym)


class symtable():
    undef = "*UND*"
    abs = "*ABS*"
    def __init__(self):
        self.table = {}
        self.sections = {"*ABS*":["*ABS*",0,0,0],"*UND*":["*UND*",0,0,0]}
    def add(self, name, size, addr, sect):
        #print("<<adding",name,size,addr,sect)
        if name.startswith("."):
            self.sections[name]=[name,int(size,16),addr,0]
        else:
            if sect=="*COM*":
                sect=".bss"
            self.table[name]=(name,int(size,16),addr,sect)
            self.sections[sect][1]+=int(size,16)
            self.sections[sect][3]+=1
    def getfrom(self,sect):
        res = {}
        for k,v in self.table.items():
            if v[3]==sect:
                res[v[0]]=v[2]
        return res
    def sizeof(self,sect):
        return self.sections[sect][1]
    def elementsof(self,sect):
        return self.sections[sect][3]
    def symbols(self):
        return frozenset(self.table.keys())
    def info(self):
        for k,v in self.sections.items():
            print(k,":",v[1],"@",v[2],"#",v[3])
        for k,v in self.table.items():
            print(k,"in",v[3],v[1],"@",v[2])

#TODO: abstract for generic platform
class gcc():
    def __init__(self,tools, opts={}):
        self.gcc = tools["gcc"]
        self.gccopts = ["-c"]
        self.defines=[]
        self.incpaths=[]
        if "cflags" in opts:
            self.gccopts.extend(opts["cflags"])
        if "defs" in opts:
            self.defines = ["-D"+str(x) for x in opts["defs"]]
        if "inc" in opts:
            self.incpaths = ["-I"+str(x) for x in opts["inc"]]
        self.objdump = tools["objdump"]
        self.ld = tools["ld"]
        self.readelf = tools["readelf"]

    def run_command(self,cmd, args):
        ret = 0
        torun = [cmd]
        torun.extend(args)
        ecode,cout,cerr = proc.run(torun)
        return (ecode,cout)

    def get_headers(self,fnames):
        res = {}
        for fname in fnames:
            inc = []
            res[fname]=[]
            dirname, filename = fs.split(fname)
            if dirname:
                inc.append("-I"+dirname)
            inc.extend(self.incpaths)
            nm = [fname]
            ret, output = self.run_command(self.gcc,self.gccopts+["-M"]+inc+nm+self.defines)
            if not ret:
                lines = output.split("\n")
                for line in lines:
                    if line.endswith("\\"):
                        line=line[0:-1]
                    line=line.strip()
                    if fs.exists(line):
                        res[fname].append(line)
            return res

    def compile(self, fnames,o=None):
        wrn = {}
        err = {}
        ret = 1
        for fname in fnames:
            inc = []
            dirname, filename = fs.split(fname)
            if dirname:
                inc.append("-I"+dirname)
            inc.extend(self.incpaths)
            #print(inc)
            nm = [fname]
            if o:
                nm.append("-o")
                if not fs.isdir(o):
                    nm.append(o)
                else:
                    nm.append(fs.path(o,fs.basename(fname).replace(".c",".o")))
                    
            ret, output = self.run_command(self.gcc,self.gccopts+inc+nm+self.defines)
            lines = output.split("\n")
            catcher = re.compile("([^:]+):([0-9]+):([0-9]+):[^:]*(warning|error)(.*)")
            for line in lines:
                res = catcher.match(line)
                if res:
                    if res.group(4)=="warning":
                        cnt = wrn
                    elif res.group(4)=="error":
                        cnt = err
                    else:
                        continue
                    fname = res.group(1)
                    if fname not in cnt:
                        cnt[fname] = []
                    cnt[fname].append({
                        "type":res.group(4),
                        "line":int(res.group(2)),
                        "col":int(res.group(3)),
                        "msg":res.group(5)
                    })
            if ret!=0:
                break
        return (ret,wrn,err,output)
    def symbol_table(self,fname):
        ret = symtable()
        res, output = self.run_command(self.objdump,["-t",fname])
        output = output.replace("\t"," ")
        if res==0:
            catcher = re.compile("([0-9a-fA-F]+)([A-Za-z ]+)([^ ]+) ([0-9a-fA-F]+) ([^ ]+)")
            lines = output.split("\n")
            for line in lines:
                #print(">>",line,"<<")
                mth = catcher.match(line)
                if mth:
                    #print("matched\n")
                    ret.add(mth.group(5),mth.group(4),mth.group(1),mth.group(3))
                else:
                    pass
                    #print("not matched\n")
        return ret
    def link(self, fnames, symt={}, reloc=True, ofile=None):
        ldopt =[]
        for k,v in symt.items():
            if k.startswith("."):
                ldopt.append("--section-start="+k+"="+hex(v))
            else:
                ldopt.append("--defsym="+k+"="+hex(v))
        #ldopt.append("--gc-sections")
        if reloc:
            ldopt.append("-r")
        ldopt.extend(fnames)
        if ofile:
            ldopt.append("-o")
            ldopt.append(ofile)
        #print(ldopt)
        ret,output = self.run_command(self.ld,ldopt)
        return (ret,output)
    def generate_zerynth_binary(self,table,fname):
        res,output = self.run_command(self.objdump,["-s",fname])
        cobj = ZerynthCObj()
        if res==0:
            lines = output.replace("\t"," ").split("\n")
            bcatcher = re.compile(" ([0-9a-fA-F]+) ([0-9a-fA-F]*) ([0-9a-fA-F]*) ([0-9a-fA-F]*) ([0-9a-fA-F]*)(.*)")
            hcatcher = re.compile("Contents of section ([^:]+)")
            cursect = None
            for line in lines:
                hmth = hcatcher.match(line)
                if hmth:
                    #header line                    
                    if hmth.group(1) not in [".text",".rodata",".data"]:
                        cursect = None
                    else:
                        cursect = hmth.group(1)
                    continue
                bmth = bcatcher.match(line)
                if bmth:
                    if cursect:
                        bstr = bmth.group(2).strip()+bmth.group(3).strip()+bmth.group(4).strip()+bmth.group(5).strip()
                        bstr = [bstr[i:i + 2] for i in range(0, len(bstr), 2)]
                        for byte in bstr:
                            cobj.add_data(cursect,int(byte,16))
        cobj.finalize(table)
        #cobj.info()
        return cobj                                                
    def info(self):
        print("GCC")
        print(self.gcc)
        print(self.objdump)
        print(self.ld)
        print(self.readelf)


# cmp = gcc("tools/linux64/gcc/arm","arm-none-eabi-")
# cmp.info()
# print(cmp.compile(["linktest.c"]))
# print(cmp.link(["linktest.o"],{"_vsymbase":0x0805000,"_start":0x800000,".text":0x808000,".data":0x208000}))
# st=cmp.symbol_table("viper.vy")
# st.info()
# bin=cmp.generate_viper_binary(st,"viper.vy")
# bin.info()
