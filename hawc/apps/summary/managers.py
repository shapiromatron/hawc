from django.apps import apps

from ..common.models import BaseManager


class SummaryTableManager(BaseManager):
    assessment_relation = "assessment"

    def clonable_queryset(self, user):
        """
        Return summary tables which can cloned by a specific user
        """
        Assessment = apps.get_model("assessment", "Assessment")
        return (
            self.filter(assessment__in=Assessment.objects.all().user_can_view(user))
            .select_related("assessment")
            .order_by("assessment__name", "title")
        )


class VisualManager(BaseManager):
    assessment_relation = "assessment"

    def clonable_queryset(self, user):
        """
        Return visuals which can cloned by a specific user
        """
        Assessment = apps.get_model("assessment", "Assessment")
        return (
            self.filter(assessment__in=Assessment.objects.all().user_can_view(user))
            .select_related("assessment")
            .order_by("assessment__name", "title")
        )
