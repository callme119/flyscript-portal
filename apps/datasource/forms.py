# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the
# MIT License set forth at:
#   https://github.com/riverbed/flyscript-portal/blob/master/LICENSE ("License").
# This software is distributed "AS IS" as set forth in the License.

from django import forms

from apps.datasource.models import Device


class DeviceDetailForm(forms.ModelForm):
    class Meta:
        model = Device

    def __init__(self, *args, **kwargs):
        # for existing model instances, change name and module fields
        # to read-only, to avoid user from editing those values easily
        super(DeviceDetailForm, self).__init__(*args, **kwargs)

        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields['name'].widget.attrs['readonly'] = True
            self.fields['module'].widget.attrs['readonly'] = True
            self.fields['password'].widget.input_type = 'password'

    def clean(self):
        # field validation only really matters if the device was enabled
        cleaned_data = super(DeviceDetailForm, self).clean()
        enabled = cleaned_data.get('enabled')

        if enabled:
            if cleaned_data.get('host').startswith('fill.in.'):
                msg = u'Please update with a valid hostname/ip address.'
                self._errors['host'] = self.error_class([msg])
                del cleaned_data['host']

            if cleaned_data.get('username') == '<username>':
                msg = u'Please enter a valid username.'
                self._errors['username'] = self.error_class([msg])
                del cleaned_data['username']

            if cleaned_data.get('password') == '<password>':
                msg = u'Please enter a valid password.'
                self._errors['password'] = self.error_class([msg])
                del cleaned_data['password']

        return cleaned_data

