Shortcuts
=========

Like [Django's shortcuts][django-shortcuts], `django_toolkit.shortcuts` provide
some helper functions to day-to-day development.

[django-shortcuts]: https://docs.djangoproject.com/en/1.10/topics/http/shortcuts/


### get_oauth2_app

`django_toolkit.shortcuts.get_oauth2_app`

Return the Application object from a *Django Rest Framework* request when
authenticated with a *Django OAuth Toolkit* access token, or return `None` when
it is not.

#### Arguments

`request`

The Django's request object


#### Example

```python
from rest_framework.decorators import api_view
from django_toolkit import shortcuts

@api_view()
def app_view(request):
    app = shortcuts.get_oauth2_app(request)
    return Response({"app": app.name})
```
