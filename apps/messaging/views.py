from typing import Any, Dict

from django.core.exceptions import BadRequest, ValidationError
from django.core.handlers.wsgi import WSGIRequest
from django.core.paginator import Paginator
from django.db.models.query import QuerySet
from django.http import HttpResponse, HttpRequest, Http404
from django.shortcuts import render
from django.urls import reverse
from django.views.generic.base import TemplateView, View
from river.models import River, RiverMembership
from river.util import get_chat_containing_river
from userauth.models import CustomUser
from userauth.util import get_system_user, get_userpair, slug_to_user

from .forms import ChatForm
from .models import Chat, Flag, Message


class ChatView(TemplateView):
    def get_template_names(self):
        if self.request.GET.get("page"):
            return ["messaging/message_list.html"]
        return super().get_template_names()

    def post(self, request: WSGIRequest, **kwargs: Dict[str, Any]) -> HttpResponse:
        """Write a new message!"""
        context = self.get_context_data(**kwargs)
        self.validate_context(context)
        chat = context["chat_ref"]
        members = context["members"]
        chat_open = context["chat_open"]
        if request.user in members and chat_open:
            if "text" in request.POST:
                return self.new_message(chat, context)
            elif "flag" in request.POST:
                return self.flag_message(context)
            elif "starter_hide" in request.POST:
                return self.hide_message(chat, context)

    def render_message(self, message: Message, context):
        request = self.request
        return render(request, "messaging/user_message_snippet.html", context)

    def get_context_data(self, **kwargs):
        """Common context data for all ChatViews"""
        context = super().get_context_data(**kwargs)
        request = self.request

        if request.user.is_authenticated:
            context["my_flags"] = list(
                map(
                    lambda f: f.message.uuid,
                    Flag.objects.filter(flagged_by=request.user),
                )
            )

        return context

    def validate_context(self, context: dict):
        """Check we have the core things in the context

        Subclasses are required to implement get_context_data and set
        certain things that we then use in this base class.
        """
        required_context_keys = ("members", "chat_ref", "chat_open")
        missing_keys = [key for key in required_context_keys if key not in context]
        if missing_keys:
            raise RuntimeError(f'missing chat context keys {", ".join(missing_keys)}')

    def new_message(self, chat: Chat, context):
        """Create the new message"""
        request = self.request
        chat_form = ChatForm(request.POST, request.FILES)
        if chat_form.is_valid():
            chat_form.full_clean()
            message = Message.objects.create(
                sender=request.user,
                text=chat_form.cleaned_data.get("text", None),
                image=chat_form.cleaned_data.get("image", None),
                file=chat_form.cleaned_data.get("file", None),
                chat=chat,
            )
            context["message"] = message
            return self.render_message(message, context)

        # TODO: should it be status 400?
        return HttpResponse(
            "<span class='block text-body text-red text-center'>Sorry, the file format not supported.</span>"
        )

    def flag_message(self, context):
        request = self.request
        message = Message.objects.get(uuid=request.POST["flag"])
        message.flagged(request.user)
        context["message"] = message
        return self.render_message(message, context)

    def hide_message(self, chat, context):
        request = self.request
        if RiverMembership.objects.filter(
            user=request.user,
            starter=True,
            river=get_chat_containing_river(chat),
        ).exists():
            message = Message.objects.get(uuid=request.POST["starter_hide"])
            message.hidden = not message.hidden
            message.hidden_reason = "by the river starter"
            message.save()
            context["message"] = message
            return self.render_message(message, context)

    def paginate_messages(
        self, request: HttpRequest, message_list: QuerySet
    ) -> Dict[str, Any]:
        # it is currently impossible to reverse pagnination order https://code.djangoproject.com/ticket/4956
        # but can include orphans: https://docs.djangoproject.com/en/4.1/ref/paginator/#django.core.paginator.Paginator.orphans
        paginator = Paginator(message_list, 10, 9)

        if request.GET.get("page"):
            page_number = request.GET.get("page")
        else:
            page_number = paginator.num_pages

        page_obj = paginator.get_page(page_number)

        total_message_count = message_list.count()

        messages_displayed_count = total_message_count - page_obj.start_index() + 1
        messages_left_count = total_message_count - messages_displayed_count

        pagination_data = {
            "page_obj": page_obj,
            "page_number": page_number,
            "messages_displayed_count": messages_displayed_count,
            "messages_left_count": messages_left_count,
        }
        return pagination_data


class ChatUpdateCheck(View):
    def get(self, request: WSGIRequest, **kwargs: Dict[str, Any]) -> HttpResponse:
        if "slug" in kwargs:
            river = River.objects.get(slug=kwargs["slug"])
            chat = river.get_chat(kwargs["stage"], kwargs["topic"])
            message_list = Message.objects.all().filter(chat=chat).order_by("timestamp")
            return HttpResponse(message_list.count())
