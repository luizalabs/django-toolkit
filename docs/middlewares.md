Middlewares
===========

> Middleware is a framework of hooks into Django’s request/response processing.
It’s a light, low-level “plugin” system for globally altering Django’s input
or output.
>
>&mdash; [Python Docs][cite]

[cite]: https://docs.djangoproject.com/pt-br/1.9/topics/http/middleware/

Middlewares must be [registered][register-middleware] in the Django's
`MIDDLEWARE_CLASSES` setting.

[register-middleware]: https://docs.djangoproject.com/pt-br/1.9/topics/http/middleware/#activating-middleware

### VersionHeaderMiddleware

`django_toolkit.middlewares.VersionHeaderMiddleware`

Adds a `X-API-Version` header to the Django's response. In order to use this
middleware, you should fill the `API_VERSION` key in the `TOOLKIT` setting.


### AccessLogMiddleware

`django_toolkit.middlewares.AccessLogMiddleware`

Create an access log entry with this format:

```
[{app_name}] {response.status_code} {request.method} {request.path}
```
