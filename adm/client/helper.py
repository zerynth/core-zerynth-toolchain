

def convert_into_job(name):
    if not name.startswith('@'):
        name = "@" + name
    return name

def from_job_name(name):
    if name.startswith('@'):
        return name[1:]
    return name