from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class ActiveLock(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    state = models.BooleanField()
    validated = models.BooleanField()
    # method = models.CharField(max_length=200, default='None')
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f'the lock state: {self.state} and set by {self.user}'

    @classmethod
    def fetchlast(cls, num, by):
        return (cls.objects.order_by('-' + by)
                   .all()[:num]
        )
