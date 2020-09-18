import json

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView

from ..common.views import MessageMixin
from . import forms, models

CACHE_DURATION = 0 if settings.DEBUG else 60 * 10


@method_decorator(cache_page(CACHE_DURATION), name="dispatch")
@method_decorator(login_required, name="dispatch")
class EhvBrowse(TemplateView):
    template_name = "vocab/ehv_browse.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["config"] = json.dumps({"data": models.Term.ehv_dataframe().to_csv(index=False)})
        return context


@method_decorator(login_required, name="dispatch")
class CreateComment(MessageMixin, CreateView):
    model = models.Comment
    form_class = forms.CommentForm
    success_message = "Your comment has been submitted!"

    def get_success_url(self):
        return self.object.last_url_visited

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(last_url_visited=self.request.META.get("HTTP_REFERER", reverse("portal")))
        return kwargs

    def form_valid(self, form):
        form.instance.commenter = self.request.user
        return super().form_valid(form)
