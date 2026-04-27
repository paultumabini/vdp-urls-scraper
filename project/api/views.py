from collections import defaultdict

from project.models import Scrape, TargetSite
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import ScrapeSerializer


def _serialize_domain_group_from_instances(scrapes):
    """Group pre-fetched Scrape rows by target domain and serialize."""
    by_domain = defaultdict(list)
    for scrape in scrapes:
        ts = scrape.target_site
        if ts and ts.site_id:
            by_domain[ts.site_id].append(scrape)
    return [
        {name: ScrapeSerializer(by_domain[name], many=True).data}
        for name in sorted(by_domain.keys())
    ]


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_scraped_items(request):
    # Enforce explicit query contract to keep response shape predictable.
    if 'webproviders' not in request.GET or 'domains' not in request.GET:
        return Response({'detail': 'Bad Request.'}, status=status.HTTP_400_BAD_REQUEST)

    webproviders_raw = (request.GET.get('webproviders') or '').strip()
    domain = (request.GET.get('domains') or '').strip()
    if not webproviders_raw or not domain:
        return Response({'detail': 'Bad Request.'}, status=status.HTTP_400_BAD_REQUEST)

    if webproviders_raw == 'available':
        providers = 'available'
    else:
        providers = [p.strip() for p in webproviders_raw.split(',') if p.strip()]
        if not providers:
            return Response({'detail': 'Bad Request.'}, status=status.HTTP_400_BAD_REQUEST)

    # Top-level payload grouped by provider, then by domain.
    web_providers_data = []

    if providers == 'available' and domain == 'all':
        all_providers = sorted(
            p
            for p in TargetSite.objects.values_list('web_provider', flat=True).distinct()
            if p
        )

        for provider in all_providers:
            scrapes = list(
                Scrape.objects.filter(spider__iexact=provider).select_related(
                    'target_site'
                )
            )
            if scrapes:
                web_providers_data.append(
                    {provider: _serialize_domain_group_from_instances(scrapes)}
                )

        return Response(web_providers_data)

    elif len(providers) >= 1 and domain == 'all':
        for provider in sorted(providers):
            scrapes = list(
                Scrape.objects.filter(spider__iexact=provider).select_related(
                    'target_site'
                )
            )
            if not scrapes:
                return Response(
                    {'detail': 'Items not found.'}, status=status.HTTP_404_NOT_FOUND
                )

            web_providers_data.append(
                {provider: _serialize_domain_group_from_instances(scrapes)}
            )

        return Response(web_providers_data)

    elif len(providers) == 1 and domain != 'all':
        # Fast path for a single provider + single domain query.
        scrapes_list = list(
            Scrape.objects.filter(
                spider__iexact=providers[0], target_site=domain
            ).select_related('target_site')
        )
        if not scrapes_list:
            return Response(
                {'detail': 'Items not found.'}, status=status.HTTP_404_NOT_FOUND
            )
        serializers = ScrapeSerializer(scrapes_list, many=True)
        site_key = (
            scrapes_list[0].target_site.site_id
            if scrapes_list[0].target_site
            else domain
        )
        sites = [{site_key: serializers.data}]
        web_providers_data.append({providers[0]: sites})
        return Response(web_providers_data)

    else:
        return Response({'detail': 'Bad Request.'}, status=status.HTTP_400_BAD_REQUEST)


