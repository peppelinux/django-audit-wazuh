def get_request_info(request):
    items = dict(request.headers.items())
    url = items.pop('Origin')  
    headers_str = ', '.join(['"{}": "{}"'.format(k, v)
                             for k,v in items if v])
    return '"url": "{}", "srcip": "{}", "path": "{}", {}'.format(url,
                                                                 request.META['REMOTE_ADDR'],
                                                                 request.get_full_path(),
                                                                 headers_str)
