import datetime

from django.core.exceptions import ValidationError


def year_validator(value):
    if value > datetime.datetime.now().year or value <= 0:
        raise ValidationError(
            f'{value} is not valid year!'
        )
