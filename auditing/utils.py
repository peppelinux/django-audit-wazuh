def get_request_info(request):
    items = dict(request.headers.items())

    # get the real ip, even if request come from a reverse proxy
    srcip = request.META['REMOTE_ADDR']
    if items.get("X-Forwarded-For") or items.get("X-Real-Ip"):
        srcip = items.get("X-Forwarded-For") or items.get("X-Real-Ip")
    
    url = request.build_absolute_uri()  
    headers_str = ', '.join(['"{}": "{}"'.format(k, v)
                             for k,v in items.items() if v])
    return '"url": "{}", "srcip": "{}", "path": "{}", {}'.format(url,
                                                                 srcip,
                                                                 request.get_full_path(),
                                                                 headers_str)
