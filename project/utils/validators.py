from django.core.validators import URLValidator


class CustomURLValidator(URLValidator):
    schemes = ['http', 'https', 'ftp', 'ftps', 'smb']
