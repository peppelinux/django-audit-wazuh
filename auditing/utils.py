import json
try:
    # TODO: Should we add ipware as a hard dependency?
    # It provides some good features which coule be handy for this library
    from ipware import get_client_ip
except ImportError:
    get_client_ip = None


def format_log_message(msg_data):
    """
    :param msg_data: The data message data dict to write as JSON
    :return: A valid json string without outer brackets to be passed to the
    python logger
    """
    return json.dumps(msg_data)[1:-1]


def get_request_info(request):
    """
    :param request: The django request object
    :return: A dictionary that contains the required fields for our siem msg
    """
    r_head = dict(request.headers.items())

    if get_client_ip:
        srcip, is_routable = get_client_ip(request)
    else:
        srcip = request.META['REMOTE_ADDR']
        srcip = r_head.get("X-Forwarded-For") or r_head.get("X-Real-Ip", srcip)

    url = request.build_absolute_uri()
    msg_data = {
        "url": url,
        "srcip": str(srcip),
        "path": request.get_full_path(),
    }
    msg_data.update(r_head)
    return msg_data
