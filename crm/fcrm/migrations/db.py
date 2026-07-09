import pymysql


def get_old_db():
    return pymysql.connect(
        host="host.docker.internal",
        user="root",
        password="",
        database="old_crm_dta",
        cursorclass=pymysql.cursors.DictCursor,
    )