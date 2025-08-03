
from django.db import models
from django.conf import settings


class Transaction(models.Model):
    STATUS_CHOICES = [
        ('INIT', 'Started'),
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Successful'),
        ('FAIL', 'Failed'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments_transactions',default=1)
    amount = models.PositiveIntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='INIT')
    authority = models.CharField(max_length=128, null=True, blank=True)
    ref_id = models.CharField(max_length=128, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transaction {self.id} - {self.status}"
