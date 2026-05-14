from django.http import HttpResponse


def robots_txt(_request: object) -> HttpResponse:
    content = "User-agent: *\nDisallow: /admin/\n"
    return HttpResponse(content, content_type="text/plain")
