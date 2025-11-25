
import os
import sys
import django


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'braincomua')))

os.environ['DJANGO_SETTINGS_MODULE'] = 'braincomua.settings'

django.setup()