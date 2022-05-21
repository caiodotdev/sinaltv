from django import forms
from django.forms import ModelForm, inlineformset_factory
from app.utils import generate_bootstrap_widgets_for_all_fields

from . import (
    models
)

class BaseForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(BaseForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            # field.widget.attrs['class'] = 'form-control'
            if field_name == 'phone' or field_name == 'telefone':
                field.widget.attrs['class'] = 'form-control telefone phone'
            if field_name == 'cep' or field_name == 'postalcode':
                field.widget.attrs['class'] = 'form-control cep'


class CategoryForm(BaseForm, ModelForm):
    class Meta:
        model = models.Category
        fields = ("id", "name")
        widgets = generate_bootstrap_widgets_for_all_fields(models.Category)

    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)


class CategoryFormToInline(BaseForm, ModelForm):
    class Meta:
        model = models.Category
        fields = ("id", "name")
        widgets = generate_bootstrap_widgets_for_all_fields(models.Category)

    def __init__(self, *args, **kwargs):
        super(CategoryFormToInline, self).__init__(*args, **kwargs)



class ChannelForm(BaseForm, ModelForm):
    class Meta:
        model = models.Channel
        fields = ("id", "title", "code", "image", "url", "link_m3u8", "category", "custom_m3u8", "program_url")
        widgets = generate_bootstrap_widgets_for_all_fields(models.Channel)

    def __init__(self, *args, **kwargs):
        super(ChannelForm, self).__init__(*args, **kwargs)


class ChannelFormToInline(BaseForm, ModelForm):
    class Meta:
        model = models.Channel
        fields = ("id", "title", "code", "image", "url", "category", "program_url")
        widgets = generate_bootstrap_widgets_for_all_fields(models.Channel)

    def __init__(self, *args, **kwargs):
        super(ChannelFormToInline, self).__init__(*args, **kwargs)


ChannelCategoryFormSet = inlineformset_factory(models.Category, models.Channel, form=ChannelFormToInline, extra=1)
