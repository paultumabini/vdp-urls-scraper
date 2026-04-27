from django import forms
from django.core.validators import RegexValidator

from .models import TargetSite


class SiteCreateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Keep placeholder choices explicit for unselected ForeignKey dropdowns.
        self.fields['site_name'].empty_label = 'select...'
        self.fields['project'].empty_label = 'select...'
        # Feed ID is optional for providers that do not expose feed metadata.
        self.fields['feed_id'].required = False
        self.label_suffix = ''  # Remove default colon from labels.

    site_url = forms.CharField(
        label='Site URL',
        max_length=50,
        validators=[
            # Validate URL-like input while allowing optional scheme from operators.
            RegexValidator(
                r'((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*',
                message='Please enter a valid web address',
            )
        ],
        widget=forms.TextInput(
            attrs={
                'placeholder': 'site url',
            }
        ),
    )
    web_provider = forms.CharField(
        label='Web Provider <i  data-html="true" class="fa fa-question-circle fa-1x red-tooltip" data-placement="top" data-toggle="tooltip" data-original-title="If a <i>web provider</i> is not available in the list, just type the <i>new one</i> and it will be automatically added into the list after submitting."></i>',
        widget=forms.TextInput(
            attrs={
                'placeholder': 'select or add...',
                'list': 'providerList',  # <datalist>
            }
        ),
    )

    site_id = forms.CharField(
        label='Domain Name',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                # Preserve explicit required attr for template-side rendering consistency.
                'required': 'true',
                'placeholder': 'domain name here',
            },
        ),
    )

    feed_id = forms.CharField(
        label='Feed ID',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'optional',
                'style': 'font-style: italic;',
            },
        ),
    )

    class Meta:
        model = TargetSite

        fields = [
            'site_name',
            'project',
            'site_url',
            'web_provider',
            'site_id',
            'feed_id',
            'note',
            'status',
            'condition',
            'unit',
            'year',
            'make',
            'model',
            'trim',
            'stock_number',
            'vin',
            'vehicle_url',
            'msrp',
            'price',
            'selling_price',
            'rebate',
            'discount',
            'images',
            'images_count',
        ]
        widgets = {
            'note': forms.Textarea(
                attrs={
                    'rows': '2',
                    'placeholder': 'Any notes or additional items to scrape, please specify here',
                }
            ),
        }
        labels = {
            'site_name': 'Site Name | Dealership',
            'project': 'Project',
            'note': 'Notes:',
            'status': 'Status',
            'condition': 'condition',
            'unit': 'as a unit',
            'year': 'year',
            'make': 'make',
            'model': 'model',
            'trim': 'trim',
            'stock_number': 'stock#',
            'vin': 'vin',
            'vehicle_url': 'vehicle url',
            'msrp': 'msrp',
            'price': 'price',
            'selling_price': 'selling price',
            'rebate': 'rebate',
            'discount': 'discount',
            'images': 'images',
            'images_count': 'images count',
        }
