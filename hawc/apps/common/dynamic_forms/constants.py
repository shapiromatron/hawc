"""Django form enums."""
from enum import Enum

from django import forms

from ..forms import InlineRadioChoiceField


class FormField(Enum):
    """Django form field enumeration.

    When removing access to a member, please
    comment out instead of omitting.
    """

    BOOLEAN = forms.BooleanField
    CHAR = forms.CharField
    CHOICE = forms.ChoiceField
    DATE = forms.DateField
    DATE_TIME = forms.DateTimeField
    DECIMAL = forms.DecimalField
    DURATION = forms.DurationField
    EMAIL = forms.EmailField
    FILE = forms.FileField
    FILEPATH = forms.FilePathField
    FLOAT = forms.FloatField
    GENERIC_IP_ADDRESS = forms.GenericIPAddressField
    IMAGE = forms.ImageField
    INTEGER = forms.IntegerField
    JSON = forms.JSONField
    MULTIPLE_CHOICE = forms.MultipleChoiceField
    NULL_BOOLEAN = forms.NullBooleanField
    REGEX = forms.RegexField
    SLUG = forms.SlugField
    TIME = forms.TimeField
    TYPED_CHOICE = forms.TypedChoiceField
    TYPED_MULTIPLE_CHOICE = forms.TypedMultipleChoiceField
    URL = forms.URLField
    UUID = forms.UUIDField
    YES_NO = InlineRadioChoiceField


class Widget(Enum):
    """Django widget enumeration.

    When removing access to a member, please
    comment out instead of omitting.
    """

    TEXT_INPUT = forms.TextInput
    NUMBER_INPUT = forms.NumberInput
    EMAIL_INPUT = forms.EmailInput
    URL_INPUT = forms.URLInput
    PASSWORD_INPUT = forms.PasswordInput
    HIDDEN_INPUT = forms.HiddenInput
    DATE_INPUT = forms.DateInput
    DATE_TIME_INPUT = forms.DateTimeInput
    TIME_INPUT = forms.TimeInput
    TEXTAREA = forms.Textarea
    CHECKBOX_INPUT = forms.CheckboxInput
    SELECT = forms.Select
    NULL_BOOLEAN_SELECT = forms.NullBooleanSelect
    SELECT_MULTIPLE = forms.SelectMultiple
    RADIO_SELECT = forms.RadioSelect
    CHECKBOX_SELECT_MULTIPLE = forms.CheckboxSelectMultiple
    FILE_INPUT = forms.FileInput
    CLEARABLE_FILE_INPUT = forms.ClearableFileInput
    MULTIPLE_HIDDEN_INPUT = forms.MultipleHiddenInput
    SPLIT_DATE_TIME = forms.SplitDateTimeWidget
    SPLIT_HIDDEN_DATE_TIME = forms.SplitHiddenDateTimeWidget
    SELECT_DATE = forms.SelectDateWidget
