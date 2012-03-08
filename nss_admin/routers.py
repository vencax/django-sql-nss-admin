
class SysAccountsRouter(object):
    """
    A router to control all database operations on models 
    in the nss_admin application
    """
    def db_for_read(self, model, **hints):
        "Point all operations on myapp models to 'other'"
        if model._meta.app_label == 'nss_admin':
            return 'sys_users'
        return None

    def db_for_write(self, model, **hints):
        "Point all operations on myapp models to 'other'"
        if model._meta.app_label == 'nss_admin':
            return 'sys_users'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        "Allow any relation if a model in myapp is involved"
        if obj1._meta.app_label == 'nss_admin' or\
           obj2._meta.app_label == 'nss_admin':
            return True
        return None

    def allow_syncdb(self, db, model):
        "Make sure the myapp app only appears on the 'other' db"
        if db == 'sys_users':
            return model._meta.app_label == 'nss_admin'
        elif model._meta.app_label == 'nss_admin':
            return False
        return None