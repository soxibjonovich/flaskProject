from flask import Flask

from models import HashStatus, Status


def capfirst(s):
    return s[0].upper() + s[1:] if s else ''


def work_status(s):
    return "Aktiv" if s == Status.Active else "Bo'sh"

def hash_status(s):
    return  "Profil chiqib ketgan" if s == HashStatus.died else "Tirik"
def nonefilter(s):
    return "hali belgilanmagan" if s is None else s


def length(s):
    return len(s)


def add_plugins(app: Flask):
    app.jinja_env.filters['capfirst'] = capfirst
    app.jinja_env.filters['length'] = length
    app.jinja_env.filters['nonefilter'] = nonefilter
    app.jinja_env.filters['work_status'] = work_status
    app.jinja_env.filters['hash_status'] = hash_status
