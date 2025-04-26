import os
import sys
import django
from django.core.management import call_command

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fighter_analysis.settings')

# Initialize Django
django.setup()

# Dump data to data.json with UTF-8 encoding, excluding contenttypes
with open('data.json', 'w', encoding='utf-8') as f:
    call_command('dumpdata', indent=2, exclude=['contenttypes'], stdout=f)
print("Data dumped successfully to data.json")