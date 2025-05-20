from django.db import models

class DJ(models.Model):
    name = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    token = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Shift(models.Model):
    title = models.CharField(max_length=200)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    venue = models.CharField(max_length=100)
    is_event = models.BooleanField(default=False)
    has_dj = models.BooleanField(default=True)
    comment = models.TextField(blank=True, null=True)
    dj = models.ForeignKey(
        DJ,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='shifts'
    )  # null = evento global

    def __str__(self):
        return f"{self.title} - {self.date} ({self.dj.name if self.dj else 'Global'})"

class Notification(models.Model):
    dj = models.ForeignKey(DJ, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.dj.name}: {self.message[:30]}"
