#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
"""this file is used to run the django project from the command line and manage the project from the command line 
if you want to run the project from the command line you can use the following command:
python manage.py runserver

if this file is not present in the project, you can create it by typing the following command:
django-admin startproject team_management

this will create a new project with the name team_management and the following files:
manage.py
settings.py
"""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Services.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
