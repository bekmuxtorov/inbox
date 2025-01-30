from django.contrib import admin
from .models import Platform, UserDetails, Operator, Ticket, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 1
    fields = ("sender_user", "sender_operator", "message_type",
              "read_status", "text", "file")
    readonly_fields = ("created_at",)


@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "updated_at")
    search_fields = ("name",)
    ordering = ("name",)
    # list_filter = ("created_at",)


@admin.register(UserDetails)
class UserDetailsAdmin(admin.ModelAdmin):
    list_display = ("user", "location", "telegram_id",
                    "platform", "created_at", "updated_at")
    search_fields = ("user__username", "location", "telegram_id")
    list_filter = ("platform", "created_at")
    ordering = ("user__username",)
    fieldsets = (
        (None, {
            'fields': ('user', 'location', 'telegram_id', 'platform')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Operator)
class OperatorAdmin(admin.ModelAdmin):
    list_display = ("full_name", "username", "created_at", "updated_at")
    search_fields = ("full_name", "username")
    list_filter = ("created_at",)
    ordering = ("full_name",)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("subject", "status", "priority", "connect_type",
                    "user_details", "operator", "created_at", "updated_at")
    list_filter = ("status", "priority", "connect_type",
                   "operator", "created_at")
    search_fields = ("subject", "user_details__user__username",
                     "operator__full_name")
    # ordering = ("created_at",)
    inlines = [MessageInline]
    fieldsets = (
        (None, {
            'fields': ('subject', 'connect_type', 'user_details', 'operator', 'status', 'priority', 'closed_at')
        }),
    )


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("ticket", "sender_user", "sender_operator",
                    "message_type", "read_status", "created_at", "updated_at")
    list_filter = ("message_type", "read_status", "sender_user",
                   "sender_operator", "created_at")
    search_fields = ("text", "ticket__subject",
                     "sender_user__user__username", "sender_operator__full_name")
    ordering = ("created_at",)
    fieldsets = (
        (None, {
            'fields': ('ticket', 'sender_user', 'sender_operator', 'message_type', 'text', 'file', 'read_status', 'reply_message')
        }),
        ('Timestamps', {
            'fields': (),
            'classes': ('collapse',)
        }),
    )
