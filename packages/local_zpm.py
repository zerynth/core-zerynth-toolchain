from base import *
from .zversions import *
from .packages import *
import sqlite3
import json
import shutil
import tarfile
import zlib
import lzma
import re
import stat

pack_url = "http://localhost/zbackend/packages/"

class Zpm():

    install_tag="__#"
    disable_tag="#__"

    def __init__(self):
        self.create_db()

    def create_db(self):
        env.load_ipack_db(env.idb,"packages.db")
        self._zdbfile = fs.path(env.zdb,"packages.db")
        self._zdb = sqlite3.connect(self._zdbfile,check_same_thread=False) if fs.exists(self._zdbfile) else None
        self._idbfile = fs.path(env.idb,"packages.db")
        self._idb = sqlite3.connect(self._idbfile,check_same_thread=False) if fs.exists(self._idbfile) else None

    def persist(self):
        self._idb.commit()

    def clear_db(self):
        if self._idb:
            self._idb.close()
            try:
                fs.rm_file(fs.path(env.idb, "packages.db"))
            except:
                pass
        self.create_db()

    def shutdown(self):
        self.persist()
        if self._idb:
            self._idb.close()       
        
    def _get_db(self,installed=False):
        if installed:
            db = self._idb
        else:
            db = self._zdb
        return db

    def _install_package(self,package, version):
        db = self._get_db(installed=True)
        if db:
            package.last_version = version
            env.put_pack(package, db)

    def _uninstall_package(self,package):
        print("deleting from db %s" % package.fullname)
        db = self._get_db(installed=True)
        if db:
            db.execute("delete from packages where uid=?",(package.uid,))
            db.commit()

    def row_to_var(self, row):
        res=Var({
                "uid":row[0],
                "fullname":row[1],
                "name":row[2],
                "description":row[3],
                "tag":row[4],
                "type":row[5],
                "authname":row[6],
                "git_pointer": row[7],
                "last_version":row[8],
                "dependencies":row[9], 
                "whatsnew":row[10],
                "rating":row[11],
                "num_of_votes":row[12],
                "num_of_downloads":row[13],
                "versions":row[14],
                "keywords":row[15],
                "last_update":row[16]
                })
        return res

    def get_all_packages(self,installed=False):
        db = self._get_db(installed)
        if db:
            for row in db.execute("""select * from packages"""):
                pack_var = self.row_to_var(row)
                pk = Package(pack_var,pack_var.uid)
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
            res = env.get_pack(fullname, db)
            if res:
                pkg = Package(res, res.uid)
                return pkg
            return None
        return None

    def _clear_tmp_folder(self):
        try:
            dirs = fs.dirs(fs.path(env.tmp))
            for dd in dirs:
                fs.rmtree(dd, env.is_windows())
            files = fs.files(fs.path(env.tmp))
            for ff in files:
                fs.rm_file(ff)
        except Exception as e:
            print("Warning:",e)


    def _download_package(self,package,version):
        #print("Downloading package %s"%package.fullname)
        p_url = pack_url+package.uid+"/"+str(version)
        headers = {"Authorization": "Bearer "+env.token}
        res = zget(url=p_url, headers=headers)
        print(res)
        if res.status_code == 200:
            fs.write_file(res.content, fs.path(env.tmp, package.name+"-"+str(version)+".tar.xz"))
            return True
        return False
    
    def get_pack_dependencies(self, pack, vers):
        pp = self.get_package(pack)
        if pp:
            dd = pp.dependencies[str(vers)]
            if dd:
                return dd
        return None

    def check_version(self, fullname, curvers, vers, curfixed, fixed, vlist):
        print("checking \t %s %s" % (fullname, curvers))
        if not isinstance(curvers, ZpmVersion):
            curvers = ZpmVersion(curvers)
        if not isinstance(vers, ZpmVersion):
            vers = ZpmVersion(vers)
        minvers = curvers.pick_min_compatible_version(vlist)
        maxvers = curvers.pick_max_compatible_version(vlist)
        if vers == curvers:
            print("RESULT \t\t same version")
            return None
        elif vers < minvers or vers > maxvers:
            print("ERROR \t\t range minvers: %s, vers: %s, maxvers: %s" % (minvers, vers, maxvers))
            return False
        elif vers >= minvers and vers <= maxvers:
            print("resolving conflict...")
            if not fixed and not curfixed:
                print("resovled \t check: %s, vers: %s" % (curvers, vers))
                if vers > curvers:
                    return None
                else:
                    return True
            elif fixed and vers > curvers:
                print("resovled \t check: %s, vers: %s" % (curvers, vers))
                return None
            elif curfixed and curvers > vers:
                print("resovled \t check: %s, vers: %s" % (curvers, vers))
                return True
            else:
                print("ERROR \t\t fixed versions check: %s, vers: %s" % (curvers, vers))
                return False

    def check_fullname(self, fullname):
        for pack in self.get_all_installed_packages():
            if fullname in pack.dependencies[str(pack.last_version)]:
                print("Cannot Remove package %s" % (fullname))
                if fullname != pack.fullname:
                    return False
        return True

    def install(self,packages,last,force):
        
        to_download = {}
        to_check = {}
        
        for pack in packages:
            pack_var = env.get_pack(pack)
            package = Package(pack_var, pack_var.uid)
            if not packages[pack] or last:
                version = package.versions[-1]
            else:
                version = ZpmVersion(packages[pack])
                if version not in package.versions:
                    raise ZpmException("no such version")
            print("Preparing \t %s %s ..." % (package.fullname,version))
            to_check.update({package.fullname:[version, True]})
        
        #read all installed packages and their versions
        installed_list = self.get_installed_list()

        #check dependencies and conflicts
        while len(to_check) > 0:
            curfullname = list(to_check.keys()).pop(0)
            curpack = self.get_package(curfullname)
            curvers,curfixed = to_check.pop(curfullname)
            
            #check conflicts
            if curpack.fullname in to_download:
                tdvers,tdfixed = to_download[curpack.fullname]
                res_check = self.check_version(curpack.fullname, curvers, tdvers, curfixed, tdfixed, curpack.versions)
                if res_check is None:
                    continue
                elif res_check is False:
                    print("fatal conflict")
                    return False
            elif curpack.fullname in installed_list:
                ivers = installed_list[curpack.fullname]
                ifixed = False
                res_check = self.check_version(curpack.fullname, curvers, ivers, curfixed, ifixed, curpack.versions)
                if res_check is None:
                    continue
                elif res_check is False:
                    print("fatal conflict")
                    return False

            #check dependencies
            deps = self.get_pack_dependencies(curpack.fullname, curvers)
            print("Check Deps \t %s %s ..." % (curpack.fullname,curvers))
            for k,v in deps.items():
                pack = self.get_package(k)
                if not pack or ZpmVersion(v) not in pack.versions:
                    print("ERROR \t\t no such dependency %s version %s"%(k,v))
                    continue #TOREMOVE
                    raise ZpmException("ERROR \t no such dependency %s version %s" % (k,v))
                if k in to_check:
                    vv = to_check[k][0]
                    fx = to_check[k][3]
                    res_check = self.check_version(k, vv, v, ff, False, pack.versions)
                    if res_check is None:
                        continue
                    elif res_check is False:
                        print("fatal conflict")
                        return False
                #append new package to check
                print("Found dep \t %s %s" % (k,v))
                if last:
                    if not isinstance(v, ZpmVersion):
                        v = ZpmVersion(v)
                    to_check.update({k:[v.pick_max_compatible_version(pack.versions),True]})
                else:
                    to_check.update({k:[v,False]})

            #append new package to dowload list
            to_download.update({curpack.fullname:[curvers, curfixed]})
        
        #download all packages from to_download list
        self._clear_tmp_folder()
        for pp in to_download:
            pack = self.get_package(pp)
            vers = to_download[pp][0]
            print("Downloading \t %s %s ..." % (pack.fullname,vers))
            res = self._download_package(pack, vers)
            if res is False:
                print("ERROR \t\t package not found %s %s" % (pack.fullname, vers))
                continue #####TOREMOVE
                return False

        #install all downloaded packages
        npkgs = len(to_download)
        npkg = 0
        for pp in to_download:
            pack = self.get_package(pp)
            vers = to_download[pp][0]
            print("Installing \t %s %s ..." % (pack.fullname,vers))
            npkg+=1
            ##### TODO restruct installation
            if pack.type=="lib":
                print("installing lib...")
                #self._install_lib(pack,vers)
            elif pack.type=="sys":
                print("installing sys...")
                #self._install_sys(pack,vers)
            elif pack.type in ("core","board","vhal","vm"):
                print("installing %s..." % pack.type)
                #self._install_core(pack,vers)
            elif pack.type == "meta":
                print("installing meta...")
                #self._install_package(pack)
            self._install_package(pack, vers)

        print("clearing tmp folder...")
        self._clear_tmp_folder()
        print("Done")  
        return True

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
                    deps = self.get_pack_dependencies(curpack.fullname, curvers)
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

    def _install_lib(self,package,version):
        #tmpdir = self._download_package(package,version)
        libdirs = package.get_folders(version)

        libdir = libdirs["path"]
        exdir  = libdirs["examples"]
        docdir = libdirs["docs"]
        tlibdir = tmpdir
        texdir = os.path.join(tmpdir,"examples")
        tdocdir = os.path.join(tmpdir,"docs","html")

        # rename already installed directories if existing
        for x in (libdir,exdir,docdir):
            try:
                #self.log("renaming %s to %s"%(x,x+Vpm.install_tag))
                os.rename(x,x+Vpm.install_tag)
            except:
                pass
        try:
            # move examples and docs and then lib
            if os.path.exists(texdir):
                #self.log("moving %s to %s"%(texdir,exdir))
                shutil.move(texdir,exdir)
            if os.path.exists(tdocdir):
                #self.log("moving %s to %s"%(tdocdir,docdir))
                shutil.move(tdocdir,docdir)
            for rm in ("package.json","main.py","readme.md","README.md","README.MD",".gitignore"):
                try:
                    os.remove(os.path.join(tlibdir,rm))
                except:
                    pass
            #self.log("moving %s to %s"%(tlibdir,libdir))
            shutil.rmtree(os.path.join(tlibdir,".git"),onerror=self.remove_readonly)
            shutil.move(tlibdir,libdir)
        except Exception as e:
            # ouch! cleanup
            shutil.rmtree(exdir,onerror=self.remove_readonly)
            shutil.rmtree(docdir,onerror=self.remove_readonly)
            shutil.rmtree(libdir,onerror=self.remove_readonly)
            for x in (libdir,exdir,docdir):
                try:
                    #self.log("renaming %s to %s"%(x+Vpm.install_tag,x))
                    os.rename(x+Vpm.install_tag,x)
                except:
                    pass
            raise e
        else:
            package.enabled = 1
            package.installed = version
            self._index_package(package,libdir)
            self._install_package(package)
            shutil.rmtree(tmpdir,onerror=self.remove_readonly)
            # remove old installed if existing
            for x in (libdir,exdir,docdir):
                #self.log("deleting %s"%(x+Vpm.install_tag))
                shutil.rmtree(x+Vpm.install_tag,onerror=self.remove_readonly)
            # remove any disabled installation dir
            for x in (libdir,exdir,docdir):
                shutil.rmtree(x+Vpm.disable_tag,onerror=self.remove_readonly)
            
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


    def _install_sys(self,package,version):
        #tmpdir = self._download_package(package,version)
        sysdirs = package.get_folders(version)
        shutil.rmtree(sysdirs["path"],onerror=self.remove_readonly)
        #os.makedirs(sysdirs["path"],exist_ok=True)
        print(package.fullname,tmpdir,package.get_json_field("targetdir",version))
        shutil.copytree(tmpdir,sysdirs["path"],ignore_dangling_symlinks=True)
        package.installed = version
        package.enabled = 1
        self._install_package(package)
        shutil.rmtree(tmpdir,onerror=self.remove_readonly)

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

    def _install_core(self,package,version):
        package.last_version = version
        ####TODO untar and move package contents to right place
        self._install_package(package)

    def update_all(self):
        print("Scanning package list...")
        installed_list = self.get_installed_list()
        self.install(packages=installed_list, last=True, force=None)