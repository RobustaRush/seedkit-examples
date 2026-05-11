import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from users.models import User


def _get_or_create_customer(user: User) -> str:
    if user.stripe_customer_id:
        return user.stripe_customer_id
    customer = stripe.Customer.create(
        email=user.email,
        idempotency_key=f"customer:user:{user.pk}",
    )
    user.stripe_customer_id = customer.id
    user.save(update_fields=["stripe_customer_id"])
    return customer.id


@login_required
def create_checkout_session(request):
    customer_id = _get_or_create_customer(request.user)  # type: ignore[arg-type]
    session = stripe.checkout.Session.create(
        customer=customer_id,
        payment_method_types=["card"],
        line_items=[{"price": request.POST["price_id"], "quantity": 1}],
        mode="subscription",
        success_url=request.build_absolute_uri("/billing/success/"),
        cancel_url=request.build_absolute_uri("/billing/cancel/"),
    )
    assert session.url
    return redirect(session.url)


@login_required
def customer_portal(request):
    user: User = request.user  # type: ignore[assignment]
    session = stripe.billing_portal.Session.create(
        customer=user.stripe_customer_id,
        return_url=request.build_absolute_uri("/billing/"),
    )
    assert session.url
    return redirect(session.url)


@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
    except (ValueError, stripe.SignatureVerificationError):
        return HttpResponse(status=400)

    if event["type"] == "customer.subscription.created":
        _handle_subscription_created(event["data"]["object"])
    elif event["type"] == "customer.subscription.deleted":
        _handle_subscription_deleted(event["data"]["object"])

    return HttpResponse(status=200)


def _handle_subscription_created(subscription):
    try:
        user = User.objects.get(stripe_customer_id=subscription["customer"])
    except User.DoesNotExist:
        return
    user.is_subscribed = True
    user.save(update_fields=["is_subscribed"])


def _handle_subscription_deleted(subscription):
    try:
        user = User.objects.get(stripe_customer_id=subscription["customer"])
    except User.DoesNotExist:
        return
    user.is_subscribed = False
    user.save(update_fields=["is_subscribed"])
