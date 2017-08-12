from base import *
from .zversions import *
import sqlite3
import json
import tarfile
import zlib
import lzma



class Zpm():

    def __init__(self):
        self._ipack_db = None
        self._zpack_db = None
        self.load_ipack_db(env.idb)
        self.load_zpack_db(env.zdb)

    def load_zpack_db(self,cfgdir,dbname="packages.db"):
        try:
            fs.makedirs(cfgdir)
            self._zpack_db_cfgdir=cfgdir
            self._zpack_db_dbname=dbname
            self._zpack_db = sqlite3.connect(fs.path(cfgdir,dbname),check_same_thread=False)
            self._zpack_db.execute("create table IF NOT EXISTS packages(uid TEXT PRIMARY KEY, fullname TEXT, title TEXT, description TEXT, type TEXT, repo TEXT, author TEXT, last_version TEXT, dependencies TEXT, whatsnew TEXT, rating REAL, num_of_votes INTEGER, num_of_downloads INTEGER, versions TEXT, keywords TEXT, last_update TEXT)")
            self._zpack_db.execute("create unique index IF NOT EXISTS packagenames on packages(fullname)")
        except Exception as e:
            warning("Error in package zdb:",e)
            self._zpack_db = None

    def clear_zpack_db(self):
        try:
            self._zpack_db.execute("delete from packages where 1")
            self._zpack_db.commit()
        except Exception as e:
            warning("Can't clear packages db!",e)

    def save_zpack_db(self):
        try:
            self._zpack_db.commit()
        except Exception as e:
            critical("can't save configuration",exc=e)

    def load_ipack_db(self,cfgdir,dbname="packages.db"):
        try:
            fs.makedirs(cfgdir)
            if self._ipack_db: 
                self._ipack_db.close()
            self._ipack_db_cfgdir=cfgdir
            self._ipack_db_dbname=dbname
            self._ipack_db = sqlite3.connect(fs.path(cfgdir,dbname),check_same_thread=False)
            self._ipack_db.execute("create table IF NOT EXISTS packages(uid TEXT PRIMARY KEY, fullname TEXT, title TEXT, description TEXT, type TEXT, repo TEXT, author TEXT, last_version TEXT, dependencies TEXT, whatsnew TEXT, rating REAL, num_of_votes INTEGER, num_of_downloads INTEGER, versions TEXT, keywords TEXT, last_update TEXT)")
            self._ipack_db.execute("create unique index IF NOT EXISTS packagenames on packages(fullname)")
        except Exception as e:
            warning("Error in package idb:",e)
            self._ipack_db = None

    def save_ipack_db(self):
        try:
            self._ipack_db.commit()
        except Exception as e:
            critical("can't save configuration",exc=e)

    def pack_from_row(self,row):
        res=Var({
            "uid":row[0],
            "fullname":row[1],
            "title":row[2],
            "description":row[3],
            "type":row[4],
            "repo":row[5],
            "author":row[6],
            "last_version":ZpmVersion(row[7]),
            "dependencies":json.loads(row[8]), 
            "whatsnew":json.loads(row[9]),
            "rating":row[10],
            "num_of_votes":row[11],
            "num_of_downloads":row[12],
            "versions":[ZpmVersion(y) for y in json.loads(row[13])],
            "keywords":json.loads(row[14]),
            "last_update":row[15]
            },recursive=False)
        return res

    def pack_to_row(self,pack):
        return (
            pack.uid,
            pack.fullname,
            pack.title,
            pack.description,
            pack.type,
            pack.repo,
            pack.author,
            str(pack.last_version),
            json.dumps(pack.dependencies),
            json.dumps(pack.whatsnew),
            pack.rating,
            pack.num_of_votes,
            pack.num_of_downloads,
            json.dumps([str(v) for v in pack.versions]),
            json.dumps(pack.keywords),
            pack.last_update
            )

    def get_pack(self, fullname, db=None):
        res = None
        if db is None:
            db = self._zpack_db
        if fullname.startswith("sys") and not fullname.endswith(env.platform): # sys packages are platform specific
            fullname=fullname+"-"+env.platform
        for row in db.execute("select * from packages where fullname=?",(fullname,)):
            res=self.pack_from_row(row)
        return res

    def put_pack(self, pack, db=None):
        if db is None:
            db = self._zpack_db
        db.execute("insert or replace into packages values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",self.pack_to_row(pack))
        db.commit()

    def _get_db(self,installed=False):
        if installed:
            db = self._ipack_db
        else:
            db = self._zpack_db
        return db

    def _install_package(self,package, version):
        db = self._get_db(installed=True)
        if db:
            package.last_version = version
            self.put_pack(package, db)

    def _uninstall_package(self,package):
        db = self._get_db(installed=True)
        if db:
            db.execute("delete from packages where uid=?",(package.uid,))
            db.commit()


    def get_all_packages(self,installed=False):
        db = self._get_db(installed)
        if db:
            for row in db.execute("""select * from packages"""):
                pk = self.pack_from_row(row)
                #pk = Package(pack_var,pack_var.uid)
                yield (pk,pk.last_version)

    def get_all_installed_packages(self):
        for pkg,v in self.get_all_packages(True):
            yield pkg

    def get_installed_list(self):
        inst_list = {}
        for pkg in self.get_all_installed_packages():
            inst_list.update({pkg.fullname:pkg.last_version})
        return inst_list

    def get_package(self,fullname,installed=False):
        db = self._get_db(installed)
        if db:
            return self.get_pack(fullname, db)
        return None

    def _clear_tmp_folder(self):
        try:
            # dirs = fs.dirs(env.tmp)
            # for dd in dirs:
            #     fs.rmtree(dd)
            # files = fs.files(env.tmp)
            # for ff in files:
            #     fs.rm_file(ff)
            pass
        except Exception as e:
            warning("Warning:",e)


    def _download_package(self,package,version,callback=None,offline=None):
        if not offline:
            res = zget(url=env.api.packages+"/"+package.fullname+"/"+str(version),stream=True,auth="conditional")
            if res.status_code == 200:
                try:
                    total_size = int(res.headers['content-length'])
                except:
                    total_size = -1
                down_data = 0
                prev_data = 0
                #TODO: test streaming for progress notification
                with open(fs.path(env.tmp, package.fullname+"-"+str(version)+".tar.xz"),"wb") as f:
                    for data in res.iter_content(chunk_size=64 * 1024):
                        f.write(data)
                        prev_data = down_data
                        down_data+=len(data)
                        if callback:
                            callback(down_data,prev_data,total_size)
                return True
            return res.status_code
        else:
            fs.copyfile(fs.path(offline,package.fullname+"-"+str(version)+".tar.xz"),fs.path(env.tmp, package.fullname+"-"+str(version)+".tar.xz"))
            return True


    def check_version(self, fullname, curvers, vers, curfixed, fixed, vlist):
        if not isinstance(curvers, ZpmVersion):
            curvers = ZpmVersion(curvers)
        if not isinstance(vers, ZpmVersion):
            vers = ZpmVersion(vers)
        minvers = curvers.pick_min_compatible_version(vlist)
        maxvers = curvers.pick_max_compatible_version(vlist)
        if vers == curvers:
            return curvers
        elif vers < minvers or vers > maxvers:
            warning("    Incompatible version",fullname,vers,"for allowed range",minvers,":",maxvers)
            return False
        elif vers >= minvers and vers <= maxvers:
            if not fixed and not curfixed:
                warning("    Selected version",vers)
                if vers > curvers:
                    return curvers
                else:
                    return vers
            elif fixed and vers > curvers:
                warning("    Selected version",vers)
                return curvers
            elif curfixed and curvers > vers:
                warning("    Selected version",vers)
                return vers
            else:
                warning("Incompatible version",fullname,vers,"vs",curvers)
                return False

    def check_fullname(self, fullname):
        for pack in self.get_all_installed_packages():
            if fullname in pack.dependencies[str(pack.last_version)]:
                print("Cannot Remove package %s" % (fullname))
                if fullname != pack.fullname:
                    return False
        return True

    def generate_installation(self,packages,last,force,justnew):
        to_download = {}
        to_check = {}
        
        # fill to_check with correct packages versions
        for pack in packages:
            package = self.get_package(pack)
            if not package:
                fatal("No such package",pack,"in package database")
            if not packages[pack] or last:
                version = package.versions[-1]
            else:
                version = ZpmVersion(packages[pack])
                if version not in package.versions:
                    raise ZpmException("no version "+str(version)+", available are "+str(package.versions))
            to_check.update({package.fullname:[version, True]})
        
        # read all installed packages and their versions
        installed_list = self.get_installed_list()

        # check dependencies and conflicts
        while to_check:
            curfullname, curval = to_check.popitem()
            curversion, curfixed = curval
            curpack = self.get_package(curfullname)
            
            # check conflicts
            if curfullname in to_download:
                tdvers,tdfixed = to_download[curfullname]
                res_check = self.check_version(curfullname, curversion, tdvers, curfixed, tdfixed, curpack.versions)
                if res_check is False:
                    return False
                elif res_check==curversion:
                    continue
            elif curfullname in installed_list and (not force and not last):
                ivers = installed_list[curfullname]
                ifixed = False
                res_check = self.check_version(curfullname, curversion, ivers, curfixed, ifixed, curpack.versions)
                if res_check is False:
                    return False
                elif res_check==curversion:
                    continue

            #check dependencies
            deps = curpack.dependencies.get(str(curversion),{})
            info("Checking dependencies of",curfullname,curversion)
            for k,v in deps.items():
                pack = self.get_package(k)
                if not pack or ZpmVersion(v) not in pack.versions:
                    info("    No such dependency",k,v)
                    if force:
                        continue
                    else:
                        raise ZpmException("no such dependency %s version %s for %s %s" % (k,v,curfullname,curversion))
                if k in to_check:
                    vv = to_check[k][0]
                    fx = to_check[k][1]
                else:
                    vv = v if not last else ZpmVersion(v).pick_max_compatible_version(pack.versions)
                    fx = False
                res_check = self.check_version(k, vv, v, curfixed, False, pack.versions)
                if res_check is False:
                    return False
                # append new package to check
                v=res_check
                info("    Selected dependency",k,v)
                if not isinstance(v, ZpmVersion):
                    v = ZpmVersion(v)
                if last:
                    to_check.update({k:[v.pick_max_compatible_version(pack.versions),True]})
                else:
                    to_check.update({k:[v,False]})

            # append new package to dowload list            
            to_download.update({curpack.fullname:[curversion, curfixed]})

        if justnew:
            ret = {k:str(v[0]) for k,v in to_download.items() if str(installed_list.get(k)) != str(v[0])}
        else:
            ret = {k:str(v[0]) for k,v in to_download.items()}
        return ret

    def install(self,to_download,callback=None,offline=None):
        #download all packages from to_download list
        if not offline:
            self._clear_tmp_folder()
        for pp in sorted(to_download):
            pack = self.get_package(pp)
            vers = to_download[pp]
            print("==>",pp)
            if pack.type=="meta":
                continue # meta packages have no files
            if offline:
                info("Downloading", pack.fullname, vers)
            else:
                info("Downloading", pack.fullname, vers)
            res = self._download_package(pack, vers,callback,offline)
            if res is not True:
                fatal("Can't download package",pack.fullname,vers,"with error",res)

        core = to_download.get("meta.zerynth.core")
    
        if core:
            # need to create a new dist
            dpath = env.dist_dir(core)
            fs.copytree(env.dist,dpath)
            #delete any patches.json in new folder
            pthfile = fs.path(dpath,"patches.json")
            if fs.exists(pthfile):
                fs.rm_file(pthfile)
            #reload installed packages db
            self.load_ipack_db(env.idb_dir(dpath))
        else:
            # no dist change
            dpath = env.dist

        env.make_dist_dirs(dpath)
        # install all downloaded packages
        for pp in to_download:
            pack = self.get_package(pp)
            vers = to_download[pp]
            pack.file = fs.path(env.tmp, pack.fullname+"-"+str(vers)+".tar.xz")
            info("Installing",pack.fullname,vers)

            if pack.type=="meta":
                self._install_package(pack,vers)
            elif pack.type=="lib":
                self._install_lib(pack,vers,dpath)
            elif pack.type=="core":
                self._install_core(pack,vers,dpath)
            elif pack.type=="board":
                self._install_device(pack,vers,dpath)
            elif pack.type=="vhal":
                self._install_vhal(pack,vers,dpath)
            elif pack.type=="sys":
                self._install_sys(pack,vers,dpath)

        self._clear_tmp_folder()
        if core:
            env.save(version=core)
            self.save_patch(dpath,core)
        return core

    def save_patch(self,path,version):
        try:
            fname = "patchbase-"+env.platform+".json"
            res = zget(url=env.patchurl+"/patches/"+version+"/"+fname,auth=False)
            if res.status_code == 200:
                npth = res.json()
                fs.set_json(npth,fs.path(path,"patches.json"))
            else:
                warning("No patches available for",version,[res.status_code])
                return
        except Exception as e:
            warning("Error while asking for patches",version,e)
            return
        

    def _install_lib(self,package,version,distpath):
        lib_src = fs.get_tempdir()
        fs.untarxz(package.file,lib_src)

        ex_src = fs.path(lib_src,"examples")
        #doc_src = fs.path(lib_src,"docs","html")
        doc_src = fs.path(lib_src,"docs")

        libsdir = env.lib_dir(distpath)
        flds = package.fullname.split(".")
        namespace = flds[1]
        name = flds[2]
        repo = package.repo
        lib_dst = fs.path(libsdir,repo,namespace,name)
        ex_dst =  fs.path(env.examples_dir(distpath), package.fullname)
        #doc_dst =  fs.path(env.docs_dir(distpath), package.fullname)

        fs.rmtree(doc_src)
        # clean directories
        fs.rmtree(lib_dst)
        fs.rmtree(ex_dst)
        #fs.rmtree(doc_dst)
        
        #if fs.exists(ex_src):
        #    fs.copytree(ex_src,ex_dst)
        #    fs.rmtree(ex_src)
        #if fs.exists(doc_src):
        #    fs.copytree(doc_src,doc_dst)
        #    fs.rmtree(doc_src)
        info("    installing in",lib_dst)
        fs.copytree(lib_src,lib_dst)

        self._install_package(package,version)
        fs.del_tempdir(lib_src)

    def _install_sys(self,package,version,distpath):
        sys_src = fs.get_tempdir()
        fs.untarxz(package.file,sys_src)
        pk = fs.get_json(fs.path(sys_src,"package.json"))
        tdir = pk["targetdir"]
        
        if package.fullname.startswith("sys.zerynth.runtime-"):
            # treat runtime with care! change dst or try first, then change
            pass
        elif package.fullname.startswith("sys.zerynth.browser-"):
            # remove package.json, not needed as a tool and interfere with nw.js
            fs.rm_file(fs.path(sys_src,"package.json"))
        dst = fs.path(env.sys,tdir)
        info("    installing in",dst)
        fs.copytree(sys_src,dst)
        self._install_package(package,version)
        fs.del_tempdir(sys_src)

    def _install_vhal(self,package,version,distpath):
        vhal_src = fs.get_tempdir()
        fs.untarxz(package.file,vhal_src)
        pk = fs.get_json(fs.path(vhal_src,"package.json"))
        tdir = pk["targetdir"]
        dst = fs.path(env.vhal_dir(distpath),tdir)
        info("    installing in",dst)
        fs.copytree(vhal_src,dst)
        self._install_package(package,version)
        fs.del_tempdir(vhal_src)

    def _install_device(self,package,version,distpath):
        dev_dst = fs.path(env.devices_dir(distpath),package.fullname.split(".")[2])
        fs.rmtree(dev_dst)
        fs.makedirs(dev_dst)
        info("    installing in",dev_dst)
        fs.untarxz(package.file,dev_dst)
        self._install_package(package,version)


    def _install_core(self,package,version,distpath):
        if package.fullname=="core.zerynth.toolchain":
            dst = env.ztc_dir(distpath)
        elif package.fullname=="core.zerynth.studio":
            dst = env.studio_dir(distpath)
        elif package.fullname=="core.zerynth.stdlib":
            dst = env.stdlib_dir(distpath)
        else:
            # just in case
            dst = fs.path(distpath,package.fullname.split(".")[2])
        info("    installing in",dst)
        fs.rmtree(dst)
        # if package.fullname =="core.zerynth.docs":
        #     src = fs.get_tempdir()
        #     fs.untarxz(package.file,src)
        #     fs.copytree(fs.path(src,"docs","html"),dst)
        #     fs.del_tempdir(src)
        # else:
        fs.untarxz(package.file,dst)
        # if package.fullname=="core.zerynth.stdlib":
        #     #move examples
        #     edst = fs.path(env.examples_dir(distpath),package.fullname)
        #     esrc = fs.path(dst,"examples")
        #     fs.rmtree(edst)
        #     fs.copytree(esrc,edst)
        #     fs.rmtree(esrc)
        if package.fullname == "core.zerynth.studio":
            #change package.json for nw.js
            packjson = {
                          "name": "Zerynth Studio",
                          "main": "index.html",
                          "window": {
                            "frame": True,
                            "min_width": 800,
                            "min_height": 600
                          },
                          "version":env.var.version,
                          "user-agent":"ide/%ver/"+env.platform
                        }
            # no icon for mac, it's already in the browser
            if not env.is_mac():
                packjson["window"].update({"icon":"img/Logo512.png"})
            fs.set_json(packjson,fs.path(dst,"package.json"))
        self._install_package(package,version)


    def _install_lib_patch(self,package,version,distpath):
        lib_src = fs.get_tempdir()
        fs.untarxz(package.file,lib_src)

        doc_src = fs.path(lib_src,"docs")

        libsdir = env.lib_dir(distpath)
        flds = package.fullname.split(".")
        namespace = flds[1]
        name = flds[2]
        repo = package.repo
        lib_dst = fs.path(libsdir,repo,namespace,name)

        fs.rmtree(doc_src)
        # clean directories
        fs.rmtree(lib_dst)
        info("    installing in",lib_dst)
        fs.copytree(lib_src,lib_dst)
        fs.del_tempdir(lib_src)
        return lib_dst, fs.path(env.lib_dir(env.dist),repo,namespace,name)

    def _install_sys_patch(self,package,version,distpath):
        sys_src = fs.get_tempdir()
        fs.untarxz(package.file,sys_src)
        pk = fs.get_json(fs.path(sys_src,"package.json"))
        tdir = pk["targetdir"]
        
        if package.fullname.startswith("sys.zerynth.runtime-"):
            # for patches there is no need for newpython hack
            tdir = tdir.replace("newpython","python")
        elif package.fullname.startswith("sys.zerynth.browser-"):
            # remove package.json, not needed as a tool and interfere with nw.js
            fs.rm_file(fs.path(sys_src,"package.json"))
            # no need for newbrowser
            tdir = tdir.replace("newbrowser","browser")
        dst = fs.path(distpath,"sys",tdir)
        info("    installing in",dst)
        fs.copytree(sys_src,dst)
        fs.del_tempdir(sys_src)
        return dst, fs.path(env.sys,tdir)

    def _install_vhal_patch(self,package,version,distpath):
        vhal_src = fs.get_tempdir()
        fs.untarxz(package.file,vhal_src)
        pk = fs.get_json(fs.path(vhal_src,"package.json"))
        tdir = pk["targetdir"]
        dst = fs.path(env.vhal_dir(distpath),tdir)
        info("    installing in",dst)
        fs.copytree(vhal_src,dst)
        fs.del_tempdir(vhal_src)
        return dst, fs.path(env.vhal_dir(env.dist),tdir)

    def _install_device_patch(self,package,version,distpath):
        dev_dst = fs.path(env.devices_dir(distpath),package.fullname.split(".")[2])
        fs.rmtree(dev_dst)
        fs.makedirs(dev_dst)
        info("    installing in",dev_dst)
        fs.untarxz(package.file,dev_dst)
        return dev_dst, fs.path(env.devices_dir(env.dist),package.fullname.split(".")[2])


    def _install_core_patch(self,package,version,distpath):
        if package.fullname=="core.zerynth.toolchain":
            dst = env.ztc_dir(distpath)
            pdst = env.ztc_dir(env.dist)
        elif package.fullname=="core.zerynth.studio":
            dst = env.studio_dir(distpath)
            pdst= env.studio_dir(env.dist)
        elif package.fullname=="core.zerynth.stdlib":
            dst = env.stdlib_dir(distpath)
            pdst = env.stdlib_dir(env.dist)
        else:
            # just in case
            dst = fs.path(distpath,package.fullname.split(".")[2])
            pdst= fs.path(env.dist,pacakge.fullname.split(".")[2])
        info("    installing in",dst)
        fs.rmtree(dst)
        fs.untarxz(package.file,dst)
        if package.fullname == "core.zerynth.studio":
            #change package.json for nw.js
            packjson = {
                          "name": "Zerynth Studio",
                          "main": "index.html",
                          "window": {
                            "frame": True,
                            "min_width": 800,
                            "min_height": 600
                          },
                          "version":env.var.version,
                          "user-agent":"ide/%ver/"+env.platform
                        }
            # no icon for mac, it's already in the browser
            if not env.is_mac():
                packjson["window"].update({"icon":"img/Logo512.png"})
            fs.set_json(packjson,fs.path(dst,"package.json"))
        return dst, pdst
    
    def _uninstall_lib(self,package):
        libdirs = package.get_folders(package.installed)
        libdir = libdirs["path"]
        exdir = libdirs["examples"]
        docdir = libdirs["docs"]
        shutil.rmtree(libdir,onerror=self.remove_readonly)
        shutil.rmtree(exdir,onerror=self.remove_readonly)
        shutil.rmtree(docdir,onerror=self.remove_readonly)
        shutil.rmtree(libdir+Vpm.disable_tag,onerror=self.remove_readonly)
        shutil.rmtree(exdir+Vpm.disable_tag,onerror=self.remove_readonly)
        shutil.rmtree(docdir+Vpm.disable_tag,onerror=self.remove_readonly)
        self._uninstall_package(package)


    def _uninstall_sys(self,package):
        #tmpdir = self._download_package(package,version)
        sysdirs = package.get_folders(package.installed)
        shutil.rmtree(sysdirs["path"],onerror=self.remove_readonly)
        self._uninstall_package(package)

    def _uninstall_core(self,package):
        #tmpdir = self._download_package(package,version)
        coredirs = package.get_folders(package.installed)
        shutil.rmtree(coredirs["path"],onerror=self.remove_readonly)
        self._uninstall_package(package)

    def uninstall(self,packages):
        
        to_uninstall = {}
        to_check = {}
        print(packages)
        for pack in packages:
            print(pack)
            package = self.get_package(pack, installed=True)
            if package is not None:
                to_check.update({package.fullname:package.last_version})
        
        #read all installed packages and their versions
        installed_list = self.get_installed_list()

        #check dependencies and conflicts
        while len(to_check) > 0:
            print("to check --> ", to_check)
            curfullname = list(to_check.keys()).pop(0)
            curpack = self.get_package(curfullname, installed=True)
            curvers = to_check.pop(curfullname)

            print("ctrl %s ..." % curfullname)

            if curpack.fullname in to_uninstall:
                continue
 
            if curpack.fullname in installed_list:
                res = self.check_fullname(curpack.fullname)
                if res:
                    deps = curpack.dependencies.get(str(curvers),{})
                    print("Check Deps \t %s %s ..." % (curpack.fullname,curvers))
                    if deps:
                        for k,v in deps.items():
                            if k not in to_check and k in installed_list:
                                to_check.update({k:v})
                    to_uninstall.update({curpack.fullname:curpack.last_version})
            else:
                print("package %s not installed" % curfullname)
        print("to uninstall --> ",to_uninstall)
        #### unistall all packages in the to_unistall list
        ##TODO: call backend PUT
        for pack in to_uninstall:
            package = self.get_package(pack, installed=True)
            if package:
                print("Uninstalling \t %s %s"%(package.fullname,package.last_version))
                ######TODO restruct unistallation
                if package.type=="lib":
                    print("uninstalling lib...")
                    #self._uninstall_lib(package)
                elif package.type in ("core","board","vhal","vm"):
                    print("uninstalling %s..." % package.type)
                    #self._uninstall_core(package)
                elif package.type=="sys":
                    print("uninstalling sys...")
                    #self._uninstall_sys
                else:
                    print("uninstalling %s..." % package.fullname)
                    #self._uninstall_package(package)
                self._uninstall_package(package)
