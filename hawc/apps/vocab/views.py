import logging

import pandas as pd
from django.conf import settings
from django.db import transaction
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, render
from django.views.generic import TemplateView

from ..animal.models import Endpoint, Experiment
from ..common.crumbs import Breadcrumb
from ..common.helper import WebappConfig, cacheable
from ..common.htmx import HtmxViewSet, action, can_edit
from ..common.views import BaseFilterList, create_object_log
from ..mgmt.constants import TaskType
from ..mgmt.models import Task
from . import filterset, models

logger = logging.getLogger(__name__)


class VocabBrowse(TemplateView):
    vocab_name: str
    vocab_context: str

    def _get_config(self) -> str:
        # get EHV in json; use cache if possible
        def get_app_config() -> str:
            return WebappConfig(
                app="animalStartup",
                page="vocabBrowserStartup",
                data={"vocab": self.vocab_name, "data": self.get_data()},
            ).model_dump_json()

        return cacheable(
            get_app_config, f"{self.vocab_name}-df-json", cache_duration=settings.CACHE_10_MIN
        )

    def get_data(self) -> pd.DataFrame: ...

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["config"] = self._get_config()
        context["breadcrumbs"] = Breadcrumb.build_crumbs(self.request.user, self.vocab_context)
        return context


class EhvBrowse(VocabBrowse):
    vocab_name = "ehv"
    template_name = "vocab/ehv_browse.html"
    vocab_context = "Environmental Health Vocabulary"

    def get_data(self) -> pd.DataFrame:
        return models.Term.ehv_dataframe().to_csv(index=False)


class ToxRefDBBrowse(VocabBrowse):
    vocab_name = "toxrefdb"
    template_name = "vocab/toxrefdb_browse.html"
    vocab_context = "ToxRefDB Vocabulary"

    def get_data(self) -> pd.DataFrame:
        return models.Term.toxrefdb_dataframe().to_csv(index=False)


class ObservationList(BaseFilterList):
    parent_model = Experiment
    model = models.Observation
    filterset_class = filterset.ObservationFilterSet
    template_name = "vocab/observation_details.html"
    paginate_by = 30

    def get_queryset(self):
        qs = super().get_queryset().filter(experiment_id=self.parent.id)
        if self.parent.guideline:
            observations = self.generate_observations(list(qs))
            return self.filterset_class.filter(self, observations)
        else:
            return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        experiment = self.parent
        data_extracted = Task.objects.filter(study_id=experiment.study.id, type=TaskType.EXTRACTION)
        context["guideline"] = self.parent.guideline
        context["data_extraction"] = data_extracted.first()
        context["experiment"] = experiment.id
        context["assessment"] = self.parent.get_assessment()
        return context

    def generate_observations(self, observations):
        # Get all GP instances pertaining to toxrefdb
        guideline_id = models.GuidelineProfile.objects.get_guideline_id(self.parent.guideline)
        profiles = models.GuidelineProfile.objects.filter(
            guideline_id=guideline_id,
        ).select_related("endpoint__parent", "endpoint__parent__parent")

        # get all endpoints
        term_ids = [profile.endpoint.id for profile in profiles]
        endpoints = Endpoint.objects.filter(effect_subtype_term_id__in=term_ids)
        endpoint_dict = {e.effect_subtype_term_id: e for e in endpoints}

        # add saved observations
        data = []
        stored_endpoints = []
        for item in observations:
            item.endpoints = endpoint_dict.get(item.endpoint.id)
            data.append(item)
            stored_endpoints.append(item.endpoint)

        # generate new observations
        for profile in profiles:
            endpoint = profile.endpoint
            if endpoint not in stored_endpoints:
                endpoint_data = endpoint_dict.get(endpoint.id)
                observation = self.model.objects.default_observation(profile, endpoint_data)
                # get term inheritance
                observation.endpoints = endpoint_data
                data.append(observation)
        return data


class ObservationViewSet(HtmxViewSet):
    actions = {"create", "update"}
    parent_model = Experiment
    model = models.Observation
    form_fragment = "vocab/fragments/observation_form.html"
    detail_fragment = "vocab/observation_detail.html"

    @action(methods=("get", "post"), permission=can_edit)
    def create(self, request: HttpRequest, *args, **kwargs):
        if request.method == "POST":
            endpoint_id = self.request.GET.get("endpoint")
            instance = self.model.objects.filter(
                experiment=request.item.parent, endpoint=endpoint_id
            ).first()

            if instance:
                self.perform_update(request, instance, "Update", kwargs["status"])
            else:
                term = get_object_or_404(models.Term, pk=endpoint_id)
                instance = models.Observation(endpoint=term, experiment=request.item.parent)
                self.perform_update(request, instance, "Create", kwargs["status"])
        return render(
            request, self.form_fragment, self.get_context_data(instance, request, kwargs["status"])
        )

    @transaction.atomic
    def perform_update(self, request, instance, action, status):
        checkbox = f"{instance.endpoint.id}-{status}"

        # Get default statuses for an object
        guideline_id = models.GuidelineProfile.objects.get_guideline_id(
            instance.experiment.guideline
        )
        profile = models.GuidelineProfile.objects.filter(
            guideline_id=guideline_id, endpoint_id=instance.endpoint.id
        ).first()
        endpoint = Endpoint.objects.filter(effect_subtype_term_id=instance.endpoint.id).first()
        default = self.model.objects.default_observation(profile, endpoint)

        # Set default attributes or update
        if action == "Create":
            instance.tested_status = default.tested_status
            instance.reported_status = default.reported_status

        if status == "tested_status":
            instance.tested_status = request.POST.get(checkbox) != "True"
        else:
            instance.reported_status = request.POST.get(checkbox) != "True"

        if action == "Update" and self.default_statuses(instance, default):
            instance.delete()
        else:
            instance.save()
            create_object_log(action, instance, request.item.assessment.id, request.user.id)

    def default_statuses(self, instance, default):
        if (
            instance.tested_status == default.tested_status
            and instance.reported_status == default.reported_status
        ):
            return True
        return False

    def get_context_data(self, instance, request, status, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object"] = instance
        context["status"] = status
        context["experiment"] = instance.experiment.id
        context["assessment"] = request.item.assessment.id
        return context
