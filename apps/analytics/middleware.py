from analytics.models import log_visit


def log_visit_middleware(get_response):
    def middleware(request):
        if request.user.is_authenticated:
            log_visit(request.user)
        response = get_response(request)
        return response

    return middleware
