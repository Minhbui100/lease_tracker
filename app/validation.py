import re
from datetime import date
from decimal import Decimal, InvalidOperation
from flask import request

EMAIL_RE=re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
PHONE_RE=re.compile(r'^\+?[\d\s().-]{7,20}$')
ZIP_RE=re.compile(r'^\d{5}(-\d{4})?$')


class FormValidator:

    def __init__(self, form):
        self.form=form
        self.errors={}

    @property
    def is_valid(self):
        return not self.errors

    def add_error(self, name, message):
        self.errors.setdefault(name, message)

    def _raw(self, name):
        return (self.form.get(name) or '').strip()

    def string(self, name, label, required=False, max_length=None, pattern=None, pattern_message=None):
        value=self._raw(name)
        if not value:
            if required:
                self.add_error(name, f'{label} is required.')
            return None
        if max_length and len(value)>max_length:
            self.add_error(name, f'{label} must be {max_length} characters or fewer.')
            return None
        if pattern and not pattern.match(value):
            self.add_error(name, pattern_message or f'{label} is not in a valid format.')
            return None
        return value

    def email(self, name, label='Email', required=False, max_length=200):
        return self.string(name, label, required, max_length, EMAIL_RE,
                           f'{label} must be a valid email address, like name@example.com.')

    def phone(self, name, label='Phone', required=False, max_length=20):
        return self.string(name, label, required, max_length, PHONE_RE,
                           f'{label} must be a valid phone number, like (555) 123-4567.')

    def integer(self, name, label, required=False, min_value=None, max_value=None):
        value=self._raw(name)
        if not value:
            if required:
                self.add_error(name, f'{label} is required.')
            return None
        try:
            number=int(value)
        except ValueError:
            self.add_error(name, f'{label} must be a whole number.')
            return None
        return self._check_range(name, label, number, min_value, max_value)

    def decimal(self, name, label, required=False, min_value=None, max_value=None, places=2):
        value=self._raw(name).replace(',', '').lstrip('$')
        if not value:
            if required:
                self.add_error(name, f'{label} is required.')
            return None
        try:
            number=Decimal(value)
        except InvalidOperation:
            self.add_error(name, f'{label} must be a number.')
            return None
        if not number.is_finite():
            self.add_error(name, f'{label} must be a number.')
            return None
        if number.as_tuple().exponent < -places:
            self.add_error(name, f'{label} can have at most {places} decimal places.')
            return None
        return self._check_range(name, label, number, min_value, max_value)

    def date(self, name, label, required=False, min_value=None, max_value=None):
        value=self._raw(name)
        if not value:
            if required:
                self.add_error(name, f'{label} is required.')
            return None
        try:
            parsed=date.fromisoformat(value)
        except ValueError:
            self.add_error(name, f'{label} must be a valid date (YYYY-MM-DD).')
            return None
        if min_value and parsed<min_value:
            self.add_error(name, f'{label} cannot be before {min_value.isoformat()}.')
            return None
        if max_value and parsed>max_value:
            self.add_error(name, f'{label} cannot be after {max_value.isoformat()}.')
            return None
        return parsed

    def choice(self, name, label, choices, required=False, default=None):
        value=self._raw(name)
        if not value:
            if required:
                self.add_error(name, f'Please select a {label.lower()}.')
            return default
        if value not in choices:
            self.add_error(name, f'Please select a valid {label.lower()}.')
            return default
        return value

    def record(self, name, label, model, required=True, query=None):
        value=self._raw(name)
        if not value:
            if required:
                self.add_error(name, f'Please select a {label.lower()}.')
            return None
        try:
            record_id=int(value)
        except ValueError:
            self.add_error(name, f'Please select a valid {label.lower()}.')
            return None
        obj=(query if query is not None else model.query).filter(model.id==record_id).first()
        if obj is None:
            self.add_error(name, f'The selected {label.lower()} is not available. Please choose another.')
        return obj

    def _check_range(self, name, label, number, min_value, max_value):
        if min_value is not None and number<min_value:
            self.add_error(name, f'{label} must be at least {min_value}.')
            return None
        if max_value is not None and number>max_value:
            self.add_error(name, f'{label} must be no more than {max_value}.')
            return None
        return number


def form_value(name, default=''):
    if request.method=='POST':
        return request.form.get(name, '')
    return '' if default is None else default


def form_values(name, defaults=()):
    if request.method=='POST':
        return request.form.getlist(name)
    return [str(d) for d in defaults]
