from django.db import models


class EmailJob(models.Model):
    recipient = models.EmailField()
    queued_at = models.DateTimeField(auto_now_add=True)
    sent = models.BooleanField(default=False)

    class Meta:
        ordering = ["-queued_at"]

    def __str__(self) -> str:
        return f"EmailJob({self.recipient})"
