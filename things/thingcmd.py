from base import *
import click
import base64


@cli.group(help="Manage connected devices (Things)")
def thing():
    pass
    


@thing.command("list",help="")
@click.option("--from","_from",default=0,type=int,help="skip the first n Things")
def __list(_from):
    table=[]
    try:
        prms = {"from":_from}
        res = zget(url=env.thing.devices,params=prms)
        rj = res.json()
        if rj["status"]=="success":
            if env.human:
                for k in rj["data"]["devices"]:
                    table.append([_from,k["platform"],k["uid"],k["token"],k["name"],k["description"],k["location"],k["geo"],k.get("groups",[]),k.get("last_seen",False),k.get("online",False),k["notifications"]])
                    _from += 1
                log_table(table,headers=[str(rj["data"]["total"]),"Target","UID","Token","Name","Desc","Location","Coords","Groups","Last Seen","Online","Notifications"])
            else:
                log_json(rj["data"])
        else:
            critical("Can't get thing list",rj["message"])
    except Exception as e:
        critical("Can't get thing list",exc=e)



@thing.command("add",help="")
@click.argument("name")
@click.option("--platform",default="",type=str)
@click.option("--location",default="",type=str)
@click.option("--description",default="",type=str)
@click.option("--lat",default=0.0, type=float)
@click.option("--lon",default=0.0, type=float)
@click.option("--tag",multiple=True, type=str)
def __add(platform,name,location,tag,lat,lon,description):
    thinfo = {
        "name":name,
        "platform":platform,
        "location":location,
        "description": description,
        "tags": tag,
        "geo": [lat,lon]
    }
    try:
        res = zpost(url=env.thing.devices, data=thinfo,timeout=20)
        rj = res.json()
        if rj["status"] == "success":
            thinfo["uid"]=rj["data"]["uid"]
            info("Thing",name,"created with uid:", thinfo["uid"])
        else:
            critical("Error while creating Thing:", rj["message"])
    except TimeoutException as e:
        critical("No answer yet")
    except Exception as e:
        critical("Can't create Thing", exc=e)




@thing.command("info",help="")
@click.argument("uid")
def __info(uid):
    try:
        res = zget(url=env.thing.config%uid)
        rj = res.json()
        if rj["status"] == "success":
            if env.human:
                table=[]
                k = rj["data"]
                table.append([k["platform"],k["uid"],k["token"],k["name"],k["description"],k["location"],k["geo"],k.get("groups",[]),k.get("last_seen"),k.get("online",False),k["notifications"]])
                log_table(table,headers=["Target","UID","Token","Name","Desc","Location","Coords","Groups","Last Seen","Online","Notifications"])
            else:
                log_json(rj["data"])
        else:
            critical("Error while getting Thing:", rj["message"])
    except TimeoutException as e:
        critical("No answer yet")
    except Exception as e:
        critical("Can't get Thing", exc=e)
    

@thing.command("config",help="")
@click.argument("uid")
@click.option("--name",default="",type=str)
@click.option("--location",default="",type=str)
@click.option("--description",default="",type=str)
@click.option("--lat",default=0.0, type=float)
@click.option("--lon",default=0.0, type=float)
@click.option("--template",default=None, type=str)
@click.option("--token",default=False,flag_value=True)
def __config(uid,name,location,description,lat,lon,template,token):
    data = {}
    if name:
        data["name"]=name
    if location:
        data["location"]=location
    if description:
        data["description"]=description
    if lat and lon:
        data["geo"]=[lat,lon]
    if template is not None:
        data["template"] = template
    if token:
        data["token"] = True
    try:
        res = zput(url=env.thing.config%uid,data=data)
        rj = res.json()
        if rj["status"] == "success":
            info("Ok")
        else:
            critical("Error while getting Thing:", rj["message"])
    except TimeoutException as e:
        critical("No answer yet")
    except Exception as e:
        critical("Can't get Thing", exc=e)



########### GROUPS

@thing.group("group",help="")
def group():
    pass

@group.command("list",help="")
@click.option("--from","_from",default=0,type=int,help="skip the first n groups")
def __groups(_from):
    table=[]
    try:
        prms = {"from":_from}
        res = zget(url=env.thing.groups,params=prms)
        rj = res.json()
        if rj["status"]=="success":
            if env.human:
                for k in rj["data"]["groups"]:
                    table.append([_from,k["uid"],k["name"],k["createdAt"]])
                    _from += 1
                log_table(table,headers=[str(rj["data"]["total"]),"UID","Group","Created"])
            else:
                log_json(rj["data"])
        else:
            critical("Can't get groups list",rj["message"])
    except Exception as e:
        critical("Can't get groups list",exc=e)

@group.command("add",help="")
@click.argument("name")
def __add_group(name):
    grinfo = {"name":name}
    try:
        res = zpost(url=env.thing.groups, data=grinfo,timeout=20)
        rj = res.json()
        if rj["status"] == "success":
            if env.human:
                info("Group",name,"created with uid",rj["data"]["uid"])
            else:
                log_json(rj["data"])
        else:
            critical("Error while creating group:", rj["message"])
    except TimeoutException as e:
        critical("No answer yet")
    except Exception as e:
        critical("Can't create group", exc=e)


@group.command("config",help="")
@click.argument("uid")
@click.option("--add",multiple=True,type=str)
@click.option("--remove",multiple=True,type=str)
def __config_group(uid,add,remove):
    data = {}    
    for x in add:
        data[x]=1
    for x in remove:
        data[x]=0
    try:
        res = zput(url=env.thing.group%uid, data=data,timeout=20)
        rj = res.json()
        if rj["status"] == "success":
            info("Ok")
        else:
            critical("Error:", rj["message"])
    except TimeoutException as e:
        critical("No answer yet")
    except Exception as e:
        critical("Can't update group", exc=e)


########### TEMPLATES

@thing.group("template",help="")
def template():
    pass


@template.command("list",help="")
@click.option("--from","_from",default=0,type=int,help="skip the first n templates")
def __templates(_from):
    table=[]
    try:
        prms = {"from":_from}
        res = zget(url=env.thing.templates,params=prms)
        rj = res.json()
        if rj["status"]=="success":
            if env.human:
                for k in rj["data"]["templates"]:
                    table.append([_from,k["uid"],k["name"],k["createdAt"]])
                    _from += 1
                log_table(table,headers=[str(rj["data"]["total"]),"UID","Name","Created"])
            else:
                log_json(rj["data"])
        else:
            critical("Can't get templates list",rj["message"])
    except Exception as e:
        critical("Can't get templates list",exc=e)


@template.command("add",help="")
@click.argument("name")
def __add_template(name):
    tminfo = {"name":name}
    try:
        res = zpost(url=env.thing.templates, data=tminfo,timeout=20)
        rj = res.json()
        if rj["status"] == "success":
            if env.human:
                info("Template",name,"created with uid:",rj["data"]["uid"])
            else:
                log_json(rj["data"])
        else:
            critical("Error while creating template:", rj["message"])
    except TimeoutException as e:
        critical("No answer yet")
    except Exception as e:
        critical("Can't create template", exc=e)


@template.command("upload",help="")
@click.argument("uid")
@click.argument("path")
def __upload_template(uid,path):
    tmpath = fs.get_tempdir()
    tmpfile =fs.path(tmpath,"template.tar.xz")
    fs.tarxz(path,tmpfile)
    content = fs.readfile(tmpfile,"b")
    fs.del_tempdir(tmpath)
    data = {
        "archive":base64.standard_b64encode(content).decode("utf8")
    } 
    try:
        res = zput(url=env.thing.template%uid, data=data,timeout=20)
        rj = res.json()
        if rj["status"] == "success":
            info("Ok")
        else:
            critical("Error:", rj["message"])
    except TimeoutException as e:
        critical("No answer yet")
    except Exception as e:
        critical("Can't update group", exc=e)