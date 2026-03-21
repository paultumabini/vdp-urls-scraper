from django.forms.models import model_to_dict
from project.models import Scrape
from rest_framework import serializers


class ScrapeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scrape
        fields = [
            'target_site',
            'category',
            'stock_number',
            'vin',
            'vehicle_url',
            'image_urls',
            'images_count',
            'unit',
            'year',
            'make',
            'model',
            'trim',
            'msrp',
            'price',
            'rebate',
            'discount',
            'last_checked',
        ]

    #  return empty string if None
    def to_representation(self, instance):
        my_fields = {field.name for field in Scrape._meta.get_fields()}
        data = super().to_representation(instance)
        for field in my_fields:
            try:
                if not data[field]:
                    data[field] = ''
            except KeyError:
                pass
        return data
