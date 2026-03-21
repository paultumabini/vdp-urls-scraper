from datetime import datetime, timedelta

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
from rest_framework.throttling import UserRateThrottle

from .serializers import ScrapeSerializer


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_scraped_items(request):

    if 'webproviders' not in request.GET or 'domains' not in request.GET:
        return Response({'detail': 'Bad Request.'}, status=status.HTTP_404_NOT_FOUND)

    providers = (
        'available'
        if request.GET.get('webproviders') == 'available'
        else request.GET.get('webproviders', False).split(',')
    )
    domain = request.GET.get('domains', False)

    # stored returned api data
    web_providers_data = []

    # filtered scrape day
    date_threshold = datetime.now() - timedelta(hours=48)

    if providers == 'available' and domain == 'all':

        all_providers = sorted(
            list({wb.web_provider for wb in TargetSite.objects.all()})
        )

        for provider in all_providers:
            scrapes = Scrape.objects.filter(
                spider__iexact=provider
            ).all()  # last_checked__gte=date_threshold

            domain_names = list(
                {
                    scrape.target_site.site_id
                    for scrape in scrapes
                    # handle `AttributeError: 'NoneType' object has no attribute 'site_id`
                    if scrape.target_site and scrape.target_site.site_id
                }
            )
            sites = []

            if scrapes:
                for name in domain_names:
                    item_data = scrapes.filter(target_site=name).all()

                    serializers = ScrapeSerializer(item_data, many=True)
                    sites.append({name: serializers.data})
                web_providers_data.append({provider: sites})

        return Response(web_providers_data)

    # resolved
    elif len(providers) >= 1 and domain == 'all':
        for provider in sorted(providers):
            scrapes = Scrape.objects.filter(
                spider__iexact=provider
            ).all()  # last_checked__gte=date_threshold
            domain_names = list({scrape.target_site.site_id for scrape in scrapes})
            sites = []

            if not scrapes:
                return Response(
                    {'detail': 'Items not found.'}, status=status.HTTP_404_NOT_FOUND
                )

            for name in domain_names:
                item_data = scrapes.filter(target_site=name).all()

                serializers = ScrapeSerializer(item_data, many=True)
                sites.append({name: serializers.data})
            web_providers_data.append({provider: sites})

        return Response(web_providers_data)

    elif len(providers) == 1 and domain != 'all':
        scrapes = Scrape.objects.filter(
            spider__iexact=providers[0], target_site=domain
        ).all()  # last_checked__gte=date_threshold
        sites = []

        if not scrapes:
            return Response(
                {'detail': 'Items not found.'}, status=status.HTTP_404_NOT_FOUND
            )

        serializers = ScrapeSerializer(scrapes, many=True)
        sites.append({scrapes[0].target_site.site_id: serializers.data})
        web_providers_data.append({providers[0]: sites})
        return Response(web_providers_data)

    else:
        return Response({'detail': 'Bad Request.'}, status=status.HTTP_400_BAD_REQUEST)


# using axios

# const searchWiki = async () => {
#     const reponse = await axios.get('http://localhost:8000/api/scraped-items/aim-dealers/', {
#     method: 'get',
#     params: {
#         webproviders: 'available',
#         domains: 'all',
#     },
#     headers: {
#         Authorization: 'Token f4b2d04a39d6fe6e4a7e04d444924daaefa33497',
#     },
#     });
#     console.log(reponse.data);
# };
