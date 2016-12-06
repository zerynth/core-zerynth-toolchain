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


@cli.command("login")
@click.option("--token",default=None)
def __login(token):
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


@cli.command()
@click.argument("email")
def reset(email):
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



@cli.command()
@click.option("--pretty","pretty",flag_value=True, default=False,help="pretty json")
@click.option("--set","__set",flag_value=True, default=False)
@click.option("--job","job",default="")
@click.option("--country","country",default="")
@click.option("--company","company",default="")
@click.option("--age","age",default="")
@click.option("--name","name",default="")
@click.option("--surname","surname",default="")
def profile(pretty,job,company,age,name,surname,country,__set):
    indent = None if not pretty else 4

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
            res = zget(url=env.api.profile)
            rj = res.json()
            if rj["status"]=="success":
                log(json.dumps(rj["data"],indent=indent))
            elif rj["code"]==403:
                log("\"Unauthorized\"")
            else:
                critical("Can't get profile",rj["message"])
        except Exception as e:
            critical("Can't get profile",e)

