import json

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import ListView, TemplateView
from django.views.generic.edit import CreateView

from ..common.views import MessageMixin, get_referrer
from . import forms, models


@method_decorator(login_required, name="dispatch")
class EhvBrowse(TemplateView):
    template_name = "vocab/ehv_browse.html"

    def _get_ehv_json(self) -> str:
        # get EHV in json; use cache if possible
        key = "ehv-dataframe-json"
        data = cache.get(key)
        if data is None:
            data = json.dumps({"data": models.Term.ehv_dataframe().to_csv(index=False)})
            cache.set(key, data, settings.CACHE_10_MIN)
        return data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["config"] = self._get_ehv_json()
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
        kwargs.update(last_url_visited=get_referrer(self.request, reverse("portal")))
        return kwargs

    def form_valid(self, form):
        form.instance.commenter = self.request.user
        return super().form_valid(form)


@method_decorator(login_required, name="dispatch")
class CommentList(ListView):
    model = models.Comment


@method_decorator(login_required, name="dispatch")
class EntityTermList(ListView):
    model = models.EntityTermRelation


@method_decorator(login_required, name="dispatch")
class ProposedEntityTermList(ListView):
    model = models.EntityTermRelation
    template_name = "vocab/proposed_entitytermrelation_list.html"

    def get_queryset(self):
        return self.model.objects.filter(approved_on=None)


@method_decorator(login_required, name="dispatch")
class TermList(ListView):
    model = models.Term
