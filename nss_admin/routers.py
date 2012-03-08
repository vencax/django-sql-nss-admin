
class SysAccountsRouter(object):
    """
    A router to control all database operations on models 
    in the SystemSQLAccounts application
    """
    def db_for_read(self, model, **hints):
        "Point all operations on myapp models to 'other'"
        if model._meta.app_label == 'SystemSQLAccounts':
            return 'sys_users'
        return None

    def db_for_write(self, model, **hints):
        "Point all operations on myapp models to 'other'"
        if model._meta.app_label == 'SystemSQLAccounts':
            return 'sys_users'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        "Allow any relation if a model in myapp is involved"
        if obj1._meta.app_label == 'SystemSQLAccounts' or\
           obj2._meta.app_label == 'SystemSQLAccounts':
            return True
        return None

    def allow_syncdb(self, db, model):
        "Make sure the myapp app only appears on the 'other' db"
        if db == 'sys_users':
            return model._meta.app_label == 'SystemSQLAccounts'
        elif model._meta.app_label == 'SystemSQLAccounts':
            return False
        return None