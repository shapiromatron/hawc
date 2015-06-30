from .staging import *

SERVER_ROLE = "production"

# There should be only minor differences from staging
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
