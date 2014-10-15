from django import forms

def form_error_list_to_ul(form):
    #Convert a list of errors from a form into a ul, used for endpoint group
    # since everything is controlled by AJAX and JSON
    txt = ['<ul>']
    for key, values in form.errors.iteritems():
        for value in values:
            if key == '__all__':
                txt.append("<li>" + value + "</li>")
            else:
                txt.append("<li>" + key + ": " + value + "</li>")
    txt.append('</ul>')
    return ' '.join(txt)


class FormsetWithIgnoredFields(forms.BaseModelFormSet):

    ignored_fields = []   # list of field names to be ignored

    def __init__(self, *args, **kwargs):
        super(FormsetWithIgnoredFields, self).__init__(*args, **kwargs)

        for i, form in enumerate(self.forms):
            for field_name in self.ignored_fields:
                value = self.data.get('form-{0}-{1}'.format(i, field_name))
                if value:
                    form.fields[field_name].initial = value
