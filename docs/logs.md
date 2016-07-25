Logs
====

Logs are critical to monitor the production environment. So we have some tools
that, even though aren't Django exclusive, helps us interact with the native
python logging module.

Filters
-------

>Filters can be used by Handlers and Loggers for more sophisticated
filtering than is provided by levels. The base filter class only allows
events which are below a certain point in the logger hierarchy.
>
>&mdash; [Python Docs][cite]

[cite]: https://docs.python.org/3/library/logging.html#filter-objects

Filters can remove some records from the output, but they also can include
additional attributes to the [LogRecord object][log-record], so that we can use
with a [formatter][log-formatter].

[log-formatter]: https://docs.python.org/3/library/logging.html#formatter-objects
[log-record]: https://docs.python.org/3/library/logging.html#logrecord-objects

Ex:

```python
LOGGING = {
    'filters': {
        'add_hostname': {
            '()': 'django_toolkit.logs.filters.AddHostName',
        }
    },
    'formatters': {
        'simple': {
            'format': '%(hostname)s %(levelname)s %(name)s %(message)s'
            # hostname is not a default LogRecord attribute
        },
    },
}
```

### AddHostName

Adds the `%(hostname)s` entry to the log record. Its `filter` method always
return `True`, so that no log record is removed from the output by this filter.

In order to use it, include a filter entry in your logging dictconfig, like
this:
```python
{
    'filters': {
        'add_hostname': {
            '()': 'django_toolkit.logs.filters.AddHostName',
        }
    },
}
```
