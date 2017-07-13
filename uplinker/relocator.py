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

    def get_relocated_code(self,symreloc,ofile,lfile,rodata_in_ram=False):
        cc = gcc(tools[self.device.cc])
        ret,output = cc.link([ofile],symreloc,reloc=False,ofile=lfile)
        if ret!=0:
            #logger.info("Relocation: %s",output)
            undf = output.count("undefined reference")
            if undf > 0:
                fatal("There are",undf,"missing symbols! This VM does not support the requested features!")
            else:
                fatal("Relocation error",output)
        sym = cc.symbol_table(lfile)
        vcobj = cc.generate_zerynth_binary(sym,lfile,rodata_in_ram)
        ##debug
        vcobj.info()
        #sym.info()
        return vcobj

    def align_to(self,x,n):
        return x if x%n==0 else x+(n-(x%n))
          
    def relocate(self,_symbols,_memstart,_romstart):
        #logger.info("Relocating Bytecode for %s",self.upl.board["shortname"])
        cc = gcc(tools[self.device.cc])
        # unpack zcode
        cobjs = self.zcode["cobjs"]
        header = bytearray(base64.standard_b64decode(self.zcode["header"]))
        pyobjs = bytearray(base64.standard_b64decode(self.zcode["pyobjs"]))
        zinfo = self.zcode["info"]
        cnatives = self.zcode["cnatives"]

        rodata_in_ram=self.device.get("rodata_in_ram",False)
        if cobjs:
            cobj = base64.standard_b64decode(cobjs)
        else:
            cobj = bytes()

        _textstart = _romstart+len(header)+len(pyobjs)
        #info("Relocation Info: memstart %x romstart %x",_memstart,_romstart)
        _textstart=self.align_to(_textstart,16)#+(16-(_textstart%16))

        if cobj:
            tmpdir = fs.get_tempdir()
            ofile = fs.path(tmpdir,"zerynth.rlo")
            lfile = fs.path(tmpdir,"zerynth.lo")
            fs.write_file(cobj,ofile)
            if len(_symbols)!=len(self.vmsym): fatal("Symbols mismatch! Expected",len(self.vmsym),"got",len(_symbols))
            symreloc = {self.vmsym[x]:_symbols[x] for x in range(0,len(_symbols))}
            symreloc.update({"_start":0,".data":_memstart,".text":_textstart})
            vcobj = self.get_relocated_code(symreloc,ofile,lfile,rodata_in_ram)
            cbin = vcobj.binary
            data_start = vcobj.romdata_start()
            data_end = vcobj.romdata_end()
            hsize = vcobj.data_bss_size()
            if rodata_in_ram and vcobj.rodata[2] and vcobj.data[2]:
                #.rodata must be copied at the end of the ram region (enlarging it)
                rodata_bin = vcobj.get_section(".rodata")
                text_bin = vcobj.get_section(".text")
                text_size = len(text_bin)
                text_pad = self.align_to(text_size,4)-text_size
                rodata_size = len(rodata_bin)
                new_rodata_start = vcobj.data[1]
                new_romdata_start = vcobj.rodata[0]+text_pad
                new_romdata_end   = vcobj.romdata[1]+text_pad
                debug("new_rodata_start",hex(new_rodata_start))
                debug("new_romdata_start",hex(new_romdata_start))
                debug("new_romdata_end",hex(new_romdata_end))
                debug("text_size/text_pad",hex(text_size),hex(text_pad))
                symreloc.update({".rodata":new_rodata_start})
                lfile2 = fs.path(tmpdir,"zerynth.lo2")
                vcobj2 = self.get_relocated_code(symreloc,ofile,lfile2,rodata_in_ram)
                text_bin = vcobj2.get_section(".text") +text_pad*b'\x00'
                cbin = text_bin+vcobj2.get_section(".data")+rodata_bin
                data_start=new_romdata_start
                data_end=new_romdata_end
                hsize+=rodata_size
                debug("ram data size",hex(hsize))

                
            # padding pyobjs
            pdsz = _textstart-_romstart-len(header)-len(pyobjs)
            for i in range(0,pdsz):
                pyobjs+=struct.pack("=B",0)
            # updating header
            header[12:16] = struct.pack("=I",_memstart)
            header[16:20] = struct.pack("=I",data_start)
            header[20:24] = struct.pack("=I",data_end)
            header[24:28] = struct.pack("=I",hsize)
            
            # updating native table
            hbg = zinfo["pyobjtable_end"]
            #logger.debug("cnatives: %i symbols: %i",len(self.upl.cnatives),len(vcobj.symbols))
            rlct = self.device.relocator
            for nn in cnatives:
                addr = vcobj.symbols[nn]
                #print(nn,hex(addr))
                #logger.info("%s => %s",tohex(addr), nn)
                # WARNING!!! +1 because it's thumb instructions! (maybe we should add thumb in arch)
                if rlct=="cortex-m":
                    header[hbg:hbg+4]=struct.pack("=I",addr+1)
                else:
                    header[hbg:hbg+4]=struct.pack("=I",addr)
                hbg+=4
            thebin = header+pyobjs+cbin
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
        # print("BSS starts at:",hex(vcobj.bss[0]))
        # print("BSS size:",vcobj.bss[2])
        # print("BSS ends at:",hex(vcobj.bss[1]))
        return thebin