from django.db import models
from django.contrib.auth.models import User, AbstractUser


class AbstractBaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Platform(AbstractBaseModel):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class UserDetails(AbstractUser, AbstractBaseModel):
    STATUS_CHOICES = [
        ("online", "Online"),
        ("offline", "Offline"),
    ]
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="online"
    )
    location = models.GenericIPAddressField(null=True, blank=True)
    telegram_id = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True
    )
    platform = models.ForeignKey(
        to=Platform,
        on_delete=models.SET_NULL,
        null=True,
        related_name="users",
    )

    groups = models.ManyToManyField(
        "auth.Group",
        related_name="user_details_groups",
        blank=True
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="user_details_permissions",
        blank=True
    )

    class Meta:
        verbose_name = 'Guest'
        verbose_name_plural = 'Guests'

    def __str__(self):
        return self.username


class Ticket(AbstractBaseModel):
    STATUS_CHOICES = [
        ("open", "Open"),
        ("in_progress", "In Progress"),
        ("closed", "Closed"),
    ]

    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
    ]
    ticket_uuid = models.UUIDField(
        verbose_name="Ticket UUID",
        max_length=16,
        unique=True
    )
    user_details = models.ForeignKey(
        UserDetails,
        on_delete=models.CASCADE,
        related_name="tickets"
    )
    operator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tickets"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="open"
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default="medium"
    )
    subject = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )
    closed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.subject[:30]} ({self.get_status_display()})"


class Message(AbstractBaseModel):
    MESSAGE_TYPE_CHOICES = [
        ("text", "Text"),
        ("image", "Image"),
        ("document", "Document"),
    ]

    sender_guest = models.ForeignKey(
        UserDetails,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="sent_messages"
    )
    sender_operator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="operator_messages"
    )
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name="messages"
    )
    text = models.TextField(null=True, blank=True)
    file = models.FileField(upload_to="messages/files/", null=True, blank=True)
    message_type = models.CharField(
        max_length=20,
        choices=MESSAGE_TYPE_CHOICES,
        default="text"
    )
    read_status = models.BooleanField(default=False)
    reply_message = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="replies"
    )

    def __str__(self):
        return f"Message {self.id} ({self.get_message_type_display()})"
