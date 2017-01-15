from base import *
from compiler import gcc
import re
import base64
import struct

class Relocator():
    def __init__(self,zcode,vm,device):
        self.zcode = zcode
        self.vmsym = []
        self.device = device
        lines = vm["symdef"].split("\n")
        for txt in lines:
            m = re.match('\s*(SYM|VAR)\((.*)\)',txt)
            if m and m.group(2):
                self.vmsym.append(m.group(2))

    def relocate(self,_symbols,_memstart,_romstart):
        #logger.info("Relocating Bytecode for %s",self.upl.board["shortname"])
        cc = gcc(tools[self.device.cc])
        # unpack zcode
        cobjs = self.zcode["cobjs"]
        header = bytearray(base64.standard_b64decode(self.zcode["header"]))
        pyobjs = bytearray(base64.standard_b64decode(self.zcode["pyobjs"]))
        zinfo = self.zcode["info"]
        cnatives = self.zcode["cnatives"]

        if cobjs:
            cobj = base64.standard_b64decode(cobjs)
        else:
            cobj = bytes()

        _textstart = _romstart+len(header)+len(pyobjs)
        #logger.info("Relocation Info: memstart %x romstart %x",_memstart,_romstart)
        if _textstart%16!=0: #align to 16
            _textstart=_textstart+(16-(_textstart%16))

        if cobj:
            tmpdir = fs.get_tempdir()
            ofile = fs.path(tmpdir,"zerynth.rlo")
            lfile = fs.path(tmpdir,"zerynth.lo")
            fs.write_file(cobj,ofile)
            if len(_symbols)!=len(self.vmsym): fatal("Symbols mismatch!")
            symreloc = {self.vmsym[x]:_symbols[x] for x in range(0,len(_symbols))}
            symreloc.update({"_start":0,".data":_memstart,".text":_textstart})
            ret,output = cc.link([ofile],symreloc,reloc=False,ofile=lfile)
            if ret!=0:
                #logger.info("Relocation: %s",output)
                undf = output.count("undefined reference")
                if undf > 0:
                    fatal("There are",undf,"missing symbols! This VM does not support the requested features!")
                else:
                    fatal("Relocation error",output)
            #backup copy for debug
            
            #logger.info("UpLinking almost done...")
            sym = cc.symbol_table(lfile)
            #logger.info("undef: %i %s",len(sym.getfrom(sym.undef)),str(sym.getfrom(sym.undef)))
            vcobj = cc.generate_zerynth_binary(sym,lfile)
            #vcobj.info()
                
            # padding pyobjs
            pdsz = _textstart-_romstart-len(header)-len(pyobjs)
            for i in range(0,pdsz):
                pyobjs+=struct.pack("=B",0)
            # updating header
            header[12:16] = struct.pack("=I",_memstart)
            if vcobj.romdata[0]:
                header[16:20] = struct.pack("=I",vcobj.romdata[0])
            else:
                header[16:20] = struct.pack("=I",0)
            if vcobj.romdata[1]:
                header[20:24] = struct.pack("=I",vcobj.romdata[1])
            else:
                header[20:24] = struct.pack("=I",0)
            hsize = 0
            if vcobj.data[2]:
                hsize+=vcobj.data[2]
            if vcobj.bss[2]:
                hsize+=vcobj.bss[2]
            header[24:28] = struct.pack("=I",hsize)
            # updating native table
            hbg = zinfo["pyobjtable_end"]
            #logger.debug("cnatives: %i symbols: %i",len(self.upl.cnatives),len(vcobj.symbols))
            rlct = self.device.relocator
            for nn in cnatives:
                addr = vcobj.symbols[nn]
                #logger.info("%s => %s",tohex(addr), nn)
                # WARNING!!! +1 because it's thumb instructions! (maybe we should add thumb in arch)
                if rlct=="cortex-m":
                    header[hbg:hbg+4]=struct.pack("=I",addr+1)
                else:
                    header[hbg:hbg+4]=struct.pack("=I",addr)
                hbg+=4
            thebin = header+pyobjs+vcobj.binary
        else:
            thebin = header+pyobjs
        
        # print("Header starts at:",hex(_romstart))
        # print("Header size:",len(self.upl.header))
        # print("Header ends at:",hex(_romstart+len(self.upl.header)))
        # print("Bytecode starts at:",hex(_romstart+len(self.upl.header)))
        # print("Bytecode size:",len(self.upl.pyobjs))
        # print("Bytecode ends at:",hex(_romstart+len(self.upl.pyobjs)+len(self.upl.header)))
        # print("Native code starts at:",hex(_textstart),"==",hex(_romstart+len(self.upl.pyobjs)+len(self.upl.header)))
        # print("Native code size:",len(vcobj.binary))
        # print("Native code ends at:",hex(_textstart+len(vcobj.binary)))
        # print("Romdata starts at:",hex(vcobj.romdata[0]))
        # print("Romdata size:",vcobj.romdata[2])
        # print("Romdata ends at:",hex(vcobj.romdata[1]))
        return thebin