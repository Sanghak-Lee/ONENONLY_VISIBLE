from django.core.exceptions import ValidationError


def validate_agreement(value):
  if value:
    return value
  else:
    raise ValidationError("필수 동의 사항")