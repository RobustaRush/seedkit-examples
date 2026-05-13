from django.db import models
from django.utils.translation import gettext_lazy as _


class JobPost(models.Model):
    title = models.CharField(_("title"), max_length=255)
    company = models.CharField(_("company"), max_length=255)
    description = models.TextField(_("description"))
    location = models.CharField(_("location"), max_length=255, blank=True)
    posted_at = models.DateTimeField(_("posted at"), auto_now_add=True)
    is_active = models.BooleanField(_("active"), default=True)

    class Meta:
        verbose_name = _("job post")
        verbose_name_plural = _("job posts")
        ordering = ["-posted_at"]

    def __str__(self):
        return f"{self.title} at {self.company}"
