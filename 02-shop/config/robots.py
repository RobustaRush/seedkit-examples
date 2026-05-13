from django.http import HttpRequest, HttpResponse


def robots_txt(request: HttpRequest) -> HttpResponse:
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Disallow: /accounts/",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")
