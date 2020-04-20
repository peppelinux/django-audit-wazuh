def get_request_info(request):
    items = dict(request.headers.items())
    url = request.build_absolute_uri()  
    headers_str = ', '.join(['"{}": "{}"'.format(k, v)
                             for k,v in items.items() if v])
    return '"url": "{}", "srcip": "{}", "path": "{}", {}'.format(url,
                                                                 request.META['REMOTE_ADDR'],
                                                                 request.get_full_path(),
                                                                 headers_str)
