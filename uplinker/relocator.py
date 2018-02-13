from base import *
from compiler import gcc
import re
import base64
import struct

class Relocator():
    def __init__(self,zcode,vm,device):
        self.zcode = zcode
        #self.vmsym = []
        self.device = device
        self.thevm = vm
        self.symtable = dict(vm["map"]["table"])

        for k in self.symtable:
            self.symtable[k]=int(self.symtable[k],16)
            #debug(k,self.symtable[k])

        self.vmsym = dict(vm["map"]["sym"])
        for k in self.vmsym:
            self.vmsym[k]=int(self.vmsym[k],16)
            #debug(k,self.vmsym[k])


        # lines = vm["symdef"].split("\n")
        # for txt in lines:
        #     m = re.match('\s*(SYM|VAR)\((.*)\)',txt)
        #     if m and m.group(2):
        #         self.vmsym.append(m.group(2))

    def get_relocated_code(self,symreloc,ofile,lfile,rodata_in_ram=False):
        cc = gcc(tools[self.device.cc])
        undf = cc.get_undefined(ofile)
        fund = set()
        srel = dict(symreloc)
        debug(undf)
        for u in undf:
            if u in self.vmsym:
                srel[u] = self.vmsym[u]
                fund.add(u)
            elif u in self.symtable:
                srel[u] = self.symtable[u]
                fund.add(u)

        #if undf!=fund:
        #    undf = undf-fund;
        #    debug("There are",len(undf),"missing symbols! This VM does not support the requested features!",undf)

        ret,output = cc.link([ofile],srel,reloc=False,ofile=lfile,abi=True)
        debug(output)
        if ret!=0:
            #logger.info("Relocation: %s",output)
            undf = output.count("undefined reference")
            if undf > 0:
                warning("There are",undf,"missing symbols! This VM does not support the requested features!")
            else:
                fatal("Relocation error",output)
        sym = cc.symbol_table(lfile)
        vcobj = cc.generate_zerynth_binary(sym,lfile,rodata_in_ram)
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
            #if len(_symbols)!=len(self.vmsym): fatal("Symbols mismatch! Expected",len(self.vmsym),"got",len(_symbols))
            symreloc = {}#dict(self.vmsym)#{self.vmsym[x]:_symbols[x] for x in range(0,len(_symbols))}
            #symreloc.update(self.vmsym)
            symreloc.update({"_start":0,".data":_memstart,".text":_textstart})
            vcobj = self.get_relocated_code(symreloc,ofile,lfile,rodata_in_ram)
            cbin = vcobj.binary
            data_start = vcobj.romdata_start()
            data_end = vcobj.romdata_end()
            hsize = vcobj.data_bss_size()
            if rodata_in_ram:
                debug("Relocation .rodata")
                #align everything to 16
                new_memstart = self.align_to(_memstart,16)
                mem_pad = new_memstart-_memstart

                acc = 0
                new_text_size  = vcobj.text[2]
                new_text_start = vcobj.text[0]
                new_text_end   = vcobj.text[1]
                new_text_pad   =  self.align_to(new_text_end,16)-new_text_end

                new_rodata_size  = vcobj.rodata_size()
                new_rodata_start = 0 if not new_rodata_size else self.align_to(vcobj.rodata_start()+mem_pad,16)  #reserve space for mem_pad
                new_rodata_end   = 0 if not new_rodata_size else new_rodata_start+new_rodata_size
                new_rodata_pad   = self.align_to(new_rodata_size,16)-new_rodata_size
                
                acc = vcobj.romdata_start() if not new_rodata_size else new_rodata_start+new_rodata_size+new_rodata_pad
                new_romdata_size  = vcobj.romdata_size()
                new_romdata_start = 0 if not new_romdata_size else self.align_to(acc,16)
                new_romdata_end   = 0 if not new_romdata_size else new_romdata_start+new_romdata_size
                new_romdata_pad   = self.align_to(new_romdata_size,16)-new_romdata_size

                new_data_size  = vcobj.data_size()
                new_data_start = 0 if not new_data_size else self.align_to(vcobj.data_start(),16)
                new_data_end   = 0 if not new_data_size else new_data_start+new_data_size
                new_data_pad   = self.align_to(new_data_size,16)-new_data_size

                acc = vcobj.bss_start() if not new_data_size else new_data_start+new_data_size+new_data_pad
                new_bss_size  = vcobj.bss_size()
                new_bss_start = 0 if not new_bss_size else self.align_to(acc,16)
                new_bss_end   = 0 if not new_bss_size else new_bss_start+new_bss_size
                new_bss_pad   = self.align_to(new_bss_size,16)-new_bss_size

                debug("Code blueprints with relocation")
                debug("text        ::",hex(new_text_start),"::",hex(new_text_end),"::",hex(new_text_size))
                debug("rodata      ::",hex(new_rodata_start),"::",hex(new_rodata_end),"::",hex(new_rodata_size),"::",hex(new_rodata_start-new_text_end))
                debug("romdata     ::",hex(new_romdata_start),"::",hex(new_romdata_end),"::",hex(new_romdata_size),"::",hex(new_romdata_start-new_text_end))
                debug("data        ::",hex(new_data_start),"::",hex(new_data_end),"::",hex(new_data_size))
                debug("bss         ::",hex(new_bss_start),"::",hex(new_bss_end),"::",hex(new_bss_size),"::",hex(new_bss_start-new_data_end))
                

                sects = {
                    ".text":new_text_start,
                    ".data":new_data_start,
                    ".romdata":new_romdata_start,
                    ".rodata":new_rodata_start,
                    ".bss":new_bss_start
                }
                symreloc.update(sects)


                # adjust data in mem
                if vcobj.rodata[2]:
                    # has rodata
                    sects.update({".rodata":new_memstart})
                    if vcobj.data[2]:
                        sects.update({".data":self.align_to(new_memstart+vcobj.rodata[2],16)})
                        if vcobj.bss[2]:
                            sects.update({".bss":self.align_to(sects[".data"]+vcobj.data[2],16)})
                    else:
                        if vcobj.bss[2]:
                            sects.update({".bss":self.align_to(new_memstart+vcobj.rodata[2],16)})
                elif vcobj.data[2]:
                    # no rodata, has data
                    sects.update({".data":new_memstart})
                    if vcobj.bss[2]:
                        sects.update({".bss":self.align_to(new_memstart+vcobj.data[2],16)})
                elif vcobj.bss[2]:
                    # only bss
                    sects.update({".bss":new_memstart})

                symreloc.update(sects)
                debug("Relocated sections")
                for k,v in sects.items():
                    debug(k,"==>",hex(v))


                ###########################################
                # text - pad - rodata - pad - romdata - pad 


                lfile2 = fs.path(tmpdir,"zerynth.lo2")
                vcobj2 = self.get_relocated_code(symreloc,ofile,lfile2,rodata_in_ram)

                fwend = new_romdata_end if new_romdata_size else new_rodata_end
                fwsize = fwend - new_text_start
                cbin = bytearray(b'\x00'*fwsize)

                cbin[0:new_text_size] = vcobj2.get_section(".text")
                prev_end = new_text_start
                if new_rodata_size:
                    cbin[new_rodata_start-new_text_start:new_rodata_end-new_text_start] = vcobj.get_section(".rodata")
                if new_romdata_size:
                    cbin[new_romdata_start-new_text_start:new_romdata_end-new_text_start] = vcobj.get_section(".data")

                if new_rodata_size:
                    data_start = new_rodata_start-mem_pad
                    data_end = new_rodata_end if not new_romdata_size else new_romdata_end
                elif  new_romdata_size:
                    data_start = new_romdata_start-mem_pad
                    data_end = new_romdata_end

                if vcobj2.bss_end() or vcobj2.data_end():
                    hsize = max(vcobj2.bss_end(),vcobj2.data_end())-_memstart
                else:
                    hsize = data_end-data_start

                debug("ram data size",hex(hsize))
                debug("binary data size",len(cbin))
                
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
