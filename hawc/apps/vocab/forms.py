from django import forms
from selectable import forms as sforms

from . import lookups


class WidgetForm(forms.Form):
    system = sforms.AutoCompleteSelectField(
        lookup_class=lookups.SystemLookup,
        label="System",
        required=True,
        widget=sforms.AutoComboboxSelectWidget,
    )
    organ = sforms.AutoCompleteSelectField(
        lookup_class=lookups.OrganLookup,
        label="Organ",
        required=True,
        widget=sforms.AutoComboboxSelectWidget,
    )
    effect = sforms.AutoCompleteSelectField(
        lookup_class=lookups.EffectLookup,
        label="Effect",
        required=True,
        widget=sforms.AutoComboboxSelectWidget,
    )
    effect_subtype = sforms.AutoCompleteSelectField(
        lookup_class=lookups.EffectSubtypeLookup,
        label="Effect Subtype",
        required=True,
        widget=sforms.AutoComboboxSelectWidget,
    )
    name = sforms.AutoCompleteSelectField(
        lookup_class=lookups.EndpointNameLookup,
        label="Endpoint name",
        required=True,
        widget=sforms.AutoComboboxSelectWidget,
    )
