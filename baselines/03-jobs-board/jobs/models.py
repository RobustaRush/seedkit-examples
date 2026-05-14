from django.db import models
from django.utils.translation import gettext_lazy as _


class Job(models.Model):
    title = models.CharField(_("title"), max_length=200)
    company = models.CharField(_("company"), max_length=200)
    description = models.TextField(_("description"))
    contact_email = models.EmailField(_("contact email"))
    published_at = models.DateTimeField(_("published at"), auto_now_add=True)
    is_active = models.BooleanField(_("active"), default=True)

    class Meta:
        verbose_name = _("job")
        verbose_name_plural = _("jobs")
        ordering = ["-published_at"]

    def __str__(self) -> str:
        return f"{self.title} at {self.company}"
