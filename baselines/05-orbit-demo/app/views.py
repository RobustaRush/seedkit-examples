from django.core.mail import send_mail
from django.http import HttpResponse


def send_test_mail(request):
    send_mail(
        subject="Orbit demo test mail",
        message="If you see this in Mailpit, the SMTP wiring works.",
        from_email=None,  # falls back to DEFAULT_FROM_EMAIL
        recipient_list=["recipient@example.com"],
    )
    return HttpResponse("Mail sent — check Mailpit at http://localhost:8025")
