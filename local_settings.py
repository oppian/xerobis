# This file is used to store your site specific settings
# for database access.
#
# Modify this file to reflect your settings, then rename it to 
# local_settings.py
#
# This file is helpful if you have an existing Django project.  
# These are specific things that Satchmo will need.
# you MUST make sure these settings are imported from your project settings file!

import os
import logging
import settings

DIRNAME = os.path.normcase(os.path.abspath(os.path.dirname(__file__)))
DEBUG = os.environ.get('DEBUG', False)


#### Satchmo unique variables ####

#These are used when loading the test data
SITE_DOMAIN = "xerobis.co.uk"
SITE_NAME = "Xerobis"


# a cache backend is required.  Do not use locmem, it will not work properly at all in production
# Preferably use memcached, but file or DB is OK.  File is faster, I don't know why you'd want to use
# db, personally.  See: http://www.djangoproject.com/documentation/cache/ for help setting up your
# cache backend

# uses env var if set otherwise mem cache
# for windows dev set CACHE_BACKEND env to "file://C:/tmp/django_cache"
if DEBUG:
	CACHE_BACKEND = 'file://C:/tmp/django_cache'
else: 
	CACHE_BACKEND = 'memcached://127.0.0.1:11211/'
	
CACHE_TIMEOUT = 60*5

ACCOUNT_ACTIVATION_DAYS = 7

# modify the cache_prefix if you have multiple concurrent stores.
CACHE_PREFIX = "STORE"

#Configure logging
LOGDIR = os.path.abspath(os.path.dirname(__file__))
LOGFILE = "satchmo.log"
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename=os.path.join(LOGDIR, LOGFILE),
                    filemode='w')

# define a Handler which writes INFO messages or higher to the sys.stderr
fileLog = logging.FileHandler(os.path.join(LOGDIR, LOGFILE), 'w')
fileLog.setLevel(logging.DEBUG)
# set a format which is simpler for console use
formatter = logging.Formatter('%(asctime)s %(name)-12s: %(levelname)-8s %(message)s')
# tell the handler to use this format
fileLog.setFormatter(formatter)
# add the handler to the root logger
logging.getLogger('').addHandler(fileLog)
logging.getLogger('keyedcache').setLevel(logging.INFO)
logging.getLogger('l10n').setLevel(logging.INFO)
logging.info("Satchmo Started")

# added as explained in http://gosatchmo.com/starting-a-new-store-real-world-project-layout
# uses satchmo templates by default unless custom one exists
SATCHMO_DIRNAME = os.path.join(DIRNAME, 'lib/satchmo/apps/satchmo_store/shop')
TEMPLATE_DIRS = (
	os.path.normcase(os.path.join(DIRNAME, "templates")),
	os.path.normcase(os.path.join(SATCHMO_DIRNAME, "templates")),
)

DEFAULT_CHARSET = 'utf-8'