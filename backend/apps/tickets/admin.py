from django.contrib import admin
from .models import Platform, UserDetails, Ticket, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 1
    fields = ("sender_guest", "sender_operator", "read_status", "text",)
    readonly_fields = ("created_at",)


@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "updated_at")
    search_fields = ("name",)
    ordering = ("name",)
    # list_filter = ("created_at",)


@admin.register(UserDetails)
class UserDetailsAdmin(admin.ModelAdmin):
    list_display = ("first_name", "location", "telegram_id",
                    "platform", "created_at", "updated_at")
    search_fields = ("location", "telegram_id", "first_name")
    list_filter = ("platform", "created_at")
    ordering = ("-created_at",)
    readonly_fields = ("location", "status", "created_at", "updated_at")
    fieldsets = (
        (None, {
            'fields': ('status', 'first_name', 'last_name', 'username', 'location', 'telegram_id', 'platform')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("ticket_uuid", "subject", "status", "priority",
                    "operator", "created_at", "updated_at")
    list_filter = ("status", "priority", "operator", "created_at")
    search_fields = ("subject", "ticket_uuid")
    ordering = ("created_at",)
    inlines = [MessageInline]
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {
            'fields': ('ticket_uuid', 'subject', 'user_details', 'operator', 'status', 'priority', 'closed_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("ticket", "sender_guest", "sender_operator",
                    "message_type", "read_status", "created_at", "updated_at")
    list_filter = ("message_type", "read_status", "sender_guest",
                   "sender_operator", "created_at")
    search_fields = ("text", "ticket__subject",)
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {
            'fields': ('ticket', 'sender_guest', 'sender_operator', 'message_type', 'text', 'file', 'read_status', 'reply_message')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
