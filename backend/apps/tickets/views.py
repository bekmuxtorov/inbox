from django.db.models import Count
from .models import Ticket
from django.views.generic import ListView, DetailView
from .models import Ticket, Platform, UserDetails, Message
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import render
from .serializers import TicketSerializer

from rest_framework import generics, status


class TicketCreateView(generics.CreateAPIView):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

    def create(self, request, *args, **kwargs):
        user = request.user
        ticket_uuid = request.data.get("ticket_uuid")

        platform, _ = Platform.objects.get_or_create(name="WEB")

        user_defaults = {
            "first_name": user.first_name if user.is_authenticated else "Guest",
            "platform": platform,
            "location": self.get_ip_from_request(request),
        }

        user_details, _ = UserDetails.objects.get_or_create(
            username=user.username if user.is_authenticated else "guest_user",
            defaults=user_defaults
        )

        existing_ticket = Ticket.objects.filter(
            ticket_uuid=ticket_uuid
        ).first()
        if existing_ticket:
            serializer = self.get_serializer(existing_ticket)
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(ticket_uuid=ticket_uuid, user_details=user_details)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_ip_from_request(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class TicketListView(ListView):
    model = Ticket
    template_name = 'tickets.html'
    context_object_name = 'tickets'

    def get_queryset(self):
        return Ticket.objects.annotate(
            message_count=Count("messages", distinct=True)
        ).filter(messages__isnull=False).order_by("-created_at")


class TicketDetailView(DetailView):
    model = Ticket
    template_name = 'ticket_detail.html'
    context_object_name = 'ticket'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ticket = self.get_object()
        messages = Message.objects.filter(
            ticket=ticket).order_by("created_at")
        tickets = Ticket.objects.annotate(
            message_count=Count("messages", distinct=True)
        ).filter(messages__isnull=False).order_by("-created_at")
        context["messages"] = messages
        context["tickets"] = tickets
        return context


def index(request):
    return render(request, "index.html")


def room(request, room_name):
    return render(request, "room.html", {"room_name": room_name})
