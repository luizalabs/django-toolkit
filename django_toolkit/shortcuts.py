# -*- coding: utf-8 -*-
def get_oauth2_app(request):
    """
    Return the Application object from a Django Rest Framework request when
    authenticated with a Django OAuth Toolkit access token, or return None
    when it is not
    """
    try:
        return request.auth.application
    except AttributeError:
        return None
