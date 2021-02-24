import json
from typing import List

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import ListView, TemplateView
from django.views.generic.edit import CreateView

from ..common.crumbs import Breadcrumb
from ..common.views import MessageMixin, get_referrer
from . import forms, models


def build_ehv_breadcrumbs(user, name: str) -> List[Breadcrumb]:
    return Breadcrumb.build_crumbs(
        user,
        name,
        [Breadcrumb(name="Environmental Health Vocabulary", url=reverse("vocab:ehv-browse"))],
    )


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
        context["breadcrumbs"] = Breadcrumb.build_crumbs(
            self.request.user, "Environmental Health Vocabulary"
        )
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = build_ehv_breadcrumbs(self.request.user, "Comment")
        return context


@method_decorator(login_required, name="dispatch")
class CommentList(ListView):
    model = models.Comment

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = build_ehv_breadcrumbs(self.request.user, "Comments")
        return context


@method_decorator(login_required, name="dispatch")
class EntityTermList(ListView):
    model = models.EntityTermRelation

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = build_ehv_breadcrumbs(self.request.user, "Entity term list")
        return context


@method_decorator(login_required, name="dispatch")
class ProposedEntityTermList(ListView):
    model = models.EntityTermRelation
    template_name = "vocab/proposed_entitytermrelation_list.html"

    def get_queryset(self):
        return self.model.objects.filter(approved_on=None)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = build_ehv_breadcrumbs(self.request.user, "Proposed relations")
        return context


@method_decorator(login_required, name="dispatch")
class TermList(ListView):
    model = models.Term

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = build_ehv_breadcrumbs(self.request.user, "Terms")
        return context
