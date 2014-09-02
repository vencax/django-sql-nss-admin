## Introduction

NIX world offers so many options to store centrally managed user accounts.
One of them is SQL DB and associated mechanism [libnss-mysql](http://libnss-mysql.sourceforge.net/configuration.shtml).
Lack of reasonable web based admins pushed me into searching if somebody has made django based admin of these entites.
There was some tries but none of them finished. Thats why this repository.
For details see [this](http://cvs.savannah.gnu.org/viewvc/nss-mysql/sample.sql?root=nss-mysql&view=markup)

User manipulation has some triggers to optionally perform some other activities.
I.e. samba user adding along sys user adding, home creating/removing.
This is done in [celery](http://www.celeryproject.org/) task to perform it asynchronously.
It is because http request processing has timelimit and this task runs pretty long.

## Installation

- Clone the read-only repo

        git clone git@github.com:vencax/django-sql-nss-admin.git

- Install the dependencies via PIP.

        pip install -r requirements.txt

- Add nss_admin into your INSTALLED_APPS.

        INSTALLED_APPS += ('nss_admin', )

- Include nss_admin.urls into your root url conf

        url(r'^nss_admin/', include('nss_admin.urls')),

- Optionaly add following configs into settings
        
        # default shell associated with a user
        DEFAULT_SHELL = '/bin/bash'
        
        # if you plan use PGina for auth on Win machines (hack - see code ..)
        PGINA_HACKS = True
        
        # begin of interval users ID taken from (prevent mangling with system account IDs)
        UID_RANGE_BEGIN = 5000
        
        # begin of interval groups ID taken from (prevent mangling with system groups IDs)
        GID_RANGE_BEGIN = 5000

plus few others (for details see. the code)



