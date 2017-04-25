import unittest
import sys
from base import *
import os

class TestZTCCommands(unittest.TestCase):

    def cmd(self,*args):
        # run ZTC
        pycmd = "python3"
        if fs.exists(fs.path(fs.homedir(),self.homepath,"sys","python")):
            if sys.platform.startswith("win"):
                pycmd = fs.path(fs.homedir(),self.homepath,"sys","python","python.exe")
            else:
                pycmd = fs.path(fs.homedir(),self.homepath,"sys","python","bin","python")
        e,out,_ = proc.run(pycmd,fs.path(fs.dirname(__file__),"..","ztc.py"),*args,outfn=log)
        return e,out

    def setUp(self):
        # create minimal setup for zerynth cfg
        self.testpath = fs.path(fs.homedir())
        if sys.platform.startswith("win"):
            self.testpath = fs.path(self.testpath,"zerynth2_test")
            self.homepath = "zerynth2"
        else:
            self.testpath = fs.path(self.testpath,".zerynth2_test")
            self.homepath = ".zerynth2"
        self.cfgdir = fs.path(self.testpath,"cfg")
        fs.makedirs(self.cfgdir)
        self.assertTrue(fs.exists(self.cfgdir))
        fs.set_json({"version":"r2.0.6"},fs.path(self.cfgdir,"config.json"))
        # create user and login, or fail
        e,out = self.cmd("register","user@zerynth.com","password","User")
        if e:
            print("LOGIN")
            e,out=self.cmd("--traceback","login","--user","user@zerynth.com","--passwd","password")
            if e:
                sys.exit(e)

    def test_user_profile(self):
        e,out = self.cmd("-J","--pretty","profile")
        self.assertEqual(e,0)

    def tearDown(self):
        fs.rmtree(self.testpath)