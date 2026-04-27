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

    def to_representation(self, instance):
        """Expose null DB values as empty strings for stable JSON (API contract)."""
        data = super().to_representation(instance)
        for key, value in data.items():
            if value is None:
                data[key] = ''
        return data
