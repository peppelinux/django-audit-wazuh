import json


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

    srcip = request.META['REMOTE_ADDR']
    srcip = r_head.get("X-Forwarded-For") or r_head.get("X-Real-Ip", srcip)

    url = request.build_absolute_uri()
    siem_data = {
        "url": url,
        "srcip": str(srcip),
        "path": request.get_full_path(),
    }
    siem_data.update(r_head)
    return siem_data
