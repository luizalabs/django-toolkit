from django.conf import settings


class VersionHeaderMiddleware(object):

    def process_response(self, request, response):
        response['X-API-Version'] = settings.TOOLKIT['API_VERSION']
        return response
