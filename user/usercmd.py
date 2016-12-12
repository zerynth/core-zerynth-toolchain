"""
.. _ztc-cmd-user:

************************
Account related commands
************************

The ZTC allows the user to authenticate against the Zerytnh backend and modify profile information.

The following commands are available:

* :ref:`login <ztc-cmd-user-login>` to retrieve an authentication token.
* :ref:`reset <ztc-cmd-user-reset>` reset to request a password reset.
* :ref:`profile <ztc-cmd-user-profile>` set and get profile information.

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


@cli.command("login",help="Obtain an authentication token")
@click.option("--token",default=None,help="set the token in non interactive mode")
def __login(token):
    """
.. _ztc-cmd-user-login:

Login
-----

The :command:`login` command enables the user to retrieve an authentication token. The token is used in most ZTC commands to communicate with the Zerynth backend.

The :command:`login` can be issued in interactive and non interactive mode. Interactive mode is started by typing: ::

    ztc login

The ZTC opens the default system browser to the login/registration page and waits for user input.

In the login/registration page, the user can login providing a valid email and the corresponding password. 
It is also possible (and faster) to login using Google plus or Facebook OAuth services. If the user do not have a Zerynth account it is possible to register
providing a valid email, a nick name and a password. Social login is also available for registration via OAuth.

Once a correct login/registration is performed, the browser will display an authentication token. Such token can be copied and pasted to the ZTC prompt.

.. warning:: multiple logins with different methods (manual or social) are allowed provided that the email linked to the social OAuth service is the same as the one used in the manual login.


Non interactive mode is started by typing: ::

    ztc login --token authentication_token

The :samp:`authentication_token` can be obtained by manually opening the login/registration `page <https://backend.zerynth.com/v1/sso>`_


.. warning:: For manual registrations, email address confirmation is needed. An email will be sent at the provided address with instructions.

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
        error("Token needed!")


@cli.command(help="Password reset. \n\n Arguments: \n\n EMAIL: email linked to the user account")
@click.argument("email")
def reset(email):
    """
.. _ztc-cmd-user-reset:

Reset Password
--------------

If a manual registration has been performed, it is possible to change the password by issuing a password reset: ::

    ztc reset email

where :samp:`email` is the email address used in the manual registration flow. An email with instruction will be sent to such address in order to allow a password change.

.. note:: on password change, all active sessions of the user will be invalidated and a new token must be retrieved.

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
.. _ztc-cmd-user-profile:

Get/Set Profile Info
--------------------

By issuing the command: ::

    ztc profile

the user profile is retrieved and displayed. The user profile consists of the following data:

* Generic Info

    * Display Name (non mutable)
    * Email (non mutable)
    * Name
    * Surname
    * Age
    * Country
    * Job
    * Company

* Subscription Info

    * Subscription type
    * Date of subscription expiration
    * List of roles
    * List of active repositories

* Asset list 

    * List of account linked assets
    * List of bought virtual machine packs


The profile  command can be used to change mutable generic info with the following syntax: ::

    ztc profile --set options

where :samp:`options` is a list of one or more of the following options: 

* :option:`--name name` update the Name field
* :option:`--surname name` update the Surname field
* :option:`--age age` update the Age field
* :option:`--country country` update the Country field
* :option:`--job job` update the Job field
* :option:`--company company` update the Company field

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
                        rj["data"]["name"],
                        rj["data"]["surname"],
                        rj["data"]["age"],
                        rj["data"]["country"],
                        rj["data"]["company"],
                        rj["data"]["job"],
                    ])
                    log()
                    info("General Info")
                    log_table(table,headers=["Display Name","Email","Name","Surname","Age","Country","Company","Job"])
                    
                    table = []
                    table.append([
                        rj["data"]["subscription"],
                        rj["data"]["pro"],
                        rj["data"]["roles"],
                        rj["data"]["repositories"]
                    ])
                    
                    log()
                    info("Account info")
                    log_table(table,headers=["Subscription","Pro Expiry","Roles","Repositories"])

                    table = []
                    freeassets = rj["data"]["assets"].get("free",[])
                    vmassets = rj["data"]["assets"].get("vm",[])
                    for asset in freeassets:
                        table.append([asset["target"],asset["current"],asset["limit"]])
                    for asset in vmassets:
                        table.append([asset["target"],asset["current"],asset["limit"]])
                    
                    log()
                    info("Assets")
                    log_table(table,headers=["target","used","max"])
                else:
                    log_json(rj["data"])
            elif rj["code"]==403:
                log("\"Unauthorized\"")
            else:
                critical("Can't get profile",rj["message"])
        except Exception as e:
            critical("Can't get profile",e)


