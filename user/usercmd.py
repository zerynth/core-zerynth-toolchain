"""
.. module:: Users

*****
Users
*****

The Zerynth User is a Database Entity collecting all account and session informations.

Every Z-User will be automaically created after a registration and can be managed and completed with some extra informations
through the following commands.

User Commands
=============

This module contains all Zerynth Toolchain Commands for managing the Zerynth User Account.
With this commands the Zerynth Users can execute the z-login (or the z-registration if first accesss) and personalize proper account informations.

In all commands is present a ``--help`` option to show to the users a brief description of the related selected command and its syntax including argument and option informations.

All commands return several log messages grouped in 4 main levels (info, warning, error, fatal) to inform the users about the results of the operation. 
The actions that can be executed on Zerynth Accounts are:

* :ref:`login<Login>`: to enter/register in proper Zerynth Account
* :ref:`reset<Reset Password>`: to reset the account password
* :ref:`profile<Change Profile Informations>`: to view or insert/modify profile informations
    """
from base import *
import click
import time
import webbrowser
import json



def check_installation():
    try:
        instfile = fs.path(env.cfg,"installation.json")
        inst = fs.get_json(instfile)
        if not inst.get("uid") and inst.get("offline",None) is not None:
            # save installation info
            try:
                res = zpost(env.api.installation,{"installer":"offline" if inst["offline"] else "online"})
                if res.status_code==200:
                    rj = res.json()
                    if rj["status"]=="success":
                        inst["uid"]=rj["data"]["inst_uid"]
                        fs.set_json(inst,instfile)
                    else:
                        warning(rj["code"],"after checking installation")
                else:
                    warning(res.status_code,"while checking installation")
            except:
                warning("Exception while sending installation data")
    except Exception as e:
        warning("Exception while checking installation",str(e))


@cli.command("login",help="Enter/Register in Zerynth Account.")
@click.option("--token",default=None,help="Token to authenticate z-user identity.")
def __login(token):
    """
Login
=====

This command is used to create a new Zerynth Account or to enter in existing one from the command line interface running: ::

    Syntax:   ./ztc login --token
    Example:  ./ztc login

This command take as input the following argument:
    * **token** (str) --> the token to authenticate the user identity (**optional**, default=None)
    
**Errors**:
    * Bad token for the authentication

.. note:: If token option not passed, the system will open the Zerynth Login/Registration web page to obtain the token.
          In this page, the user can enter the Zerynth Account through manual (username, password) or social (Google, Facebook) credentials.
          Once authenticated, the user must copy and paste the Zerynth Token value in the terminal to complete the operation.
.. warning:: For manual registrations, the email address confirmation is needed.
             The user must click on 'Verification Link' received by email to confirm the address

    """
    if not token:
        log("Hello!")
        log("In a few seconds a browser will open to the login page")
        log("Once logged, copy the authorization token and paste it here")
        time.sleep(1)
        webbrowser.open(env.api.sso)
        token = input("Paste the token here and press enter -->")
    if token:
        env.set_token(token)
        check_installation()
    else:
        error("Bad token!")


@cli.command(help="Reset the Zerynth Account Password. \n\n Arguments: \n\n EMAIL: email related to Zerynth Account")
@click.argument("email")
def reset(email):
    """
Reset Password
==============

This command is used to send a "reset account password" request to the Zerynth Backend from the command line with this syntax: ::

    Syntax:   ./ztc reset email
    Example:  ./ztc reset user@mail.com

This command take as input the following argument:
    * **email** (str) --> the email address related to the Zerynth Account (**required**)

**Errors**:
    * Missing required data
    * Receiving Zerynth Backend response errors
    * Passing email not associated to a Zerynth Account

.. note:: Once sent the request, the user will receive, via email, a "Reset Link" to complete the operation.
          Clicking on "Reset Link", the user can proceed to change the password re-entering the old one and inserting twice the new one.
    """
    try:
        res = zget(env.api.pwd_reset,auth=False,params={"email":email})
        if res.status_code!=200:
            fatal(res.status_code,"from endpoint")
        else:
            rj = res.json()
            if rj["status"]=="success":
                log("Reset instructions have been sent to",email)
            else:
                fatal("Can't reset password:",rj["message"])
    except Exception as e:
        fatal("Can't reset password:",e)



@cli.command(help="View/Insert/Modify Zerynth Account Profile Informations. \n\n")
@click.option("--set","__set",flag_value=True, default=False, help="Flag to set/modify profile informations.")
@click.option("--name","name",default="",help="Name related to the Zerynth Account.")
@click.option("--surname","surname",default="",help="Surname related to the Zerynth Account.")
@click.option("--job","job",default="",help="Job related to the Zerynth Account.")
@click.option("--country","country",default="",help="Country related to the Zerynth Account.")
@click.option("--company","company",default="",help="Company related to the Zerynth Account.")
@click.option("--age","age",default="",help="Age related to the Zerynth Account.")
def profile(job,company,age,name,surname,country,__set):
    """
Change Profile Informations
===========================

This command is used to view or insert/modify the Zerynth Account Profile Informations from the command line running: ::

    Syntax:   ./ztc profile --set --name -- surname --job --country --company --age
    Example1: ./ztc profile  
    Example2: ./ztc profile --set --name "ZUser" --company "Zerynth"

This command take as input the following arguments:
    * **set** (bool) --> flag to view, if true, or insert/modify, if false, Zerynth Account Informations (**optional**, default=False)
    * **name** (str) --> name related to the Zerynth Account (**optional**, default="")
    * **surname** (str) --> surname related to the Zerynth Account (**optional**, default="")
    * **job** (str) --> job related to the Zerynth Account (**optional**, default="")
    * **country** (str) --> country related to the Zerynth Account (**optional**, default="")
    * **company** (str) --> company related to the Zerynth Account (**optional**, default="")
    * **age** (str) --> age related to the Zerynth Account (**optional**, default="")

**Errors**:
    * Receiving Zerynth Backend response errors
    * Unauthorized Request
    """
    if __set:
        try:
            res = zput(url=env.api.profile,data = {
                "job":job,
                "company":company,
                "age":age,
                "name":name,
                "surname":surname,
                "country":country
            })
            if res.status_code!=200:
                error("Can't set profile",res.status_code)
            else:
                info("Profile set")
        except Exception as e:
            critical("Can't set profile",e)
    else:
        try:
            table=[]
            res = zget(url=env.api.profile)
            rj = res.json()
            if rj["status"]=="success":
                if env.human:
                    table.append([
                        rj["data"]["display_name"],
                        rj["data"]["email"],
                        rj["data"]["subscription"],
                        rj["data"]["pro"],
                        rj["data"]["roles"],
                        rj["data"]["repositories"],
                        rj["data"]["assets"],
                        rj["data"]["name"],
                        rj["data"]["surname"],
                        rj["data"]["job"],
                        rj["data"]["country"],
                        rj["data"]["company"],
                        rj["data"]["age"]
                    ])
                    log_table(table,headers=["Display Name","Email","Subscription","Pro Expiry","Roles","Repositories","Assets","Name","Surname","Job","Country","Company","Age"])
                else:
                    log_json(rj["data"])            
            elif rj["code"]==403:
                log("\"Unauthorized\"")
            else:
                critical("Can't get profile",rj["message"])
        except Exception as e:
            critical("Can't get profile",e)

