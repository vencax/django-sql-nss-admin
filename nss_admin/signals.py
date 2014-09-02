

def userPostSaved(sender, instance, created, **kwargs):
    from tasks import sync_user
    sync_user.delay(instance.username, getattr(instance, 'rawpwd', None))


def userPostDeleted(sender, instance, **kwargs):
    from tasks import remove_user
    remove_user.delay(instance.username)
