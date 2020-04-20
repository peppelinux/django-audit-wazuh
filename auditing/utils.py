def get_request_info(request):
    headers_str = ','.join(['{}={}'.format(k, v)
                            for k,v in request.headers.items() if v])
    return 'PATH: {} - HEADERS: {}'.format(request.get_full_path(),
                                           headers_str)
