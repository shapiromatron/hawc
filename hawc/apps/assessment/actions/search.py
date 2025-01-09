from django.contrib.contenttypes.models import ContentType
from django.db.models import Q, QuerySet
from django.db.models.base import ModelBase

from ...myuser.models import HAWCUser
from ...study.models import Study
from ..models import Assessment, Label, LabeledItem


def search_studies(
    query: str,
    all_public: bool = False,
    public: QuerySet[Assessment] | None = None,
    all_internal: bool = False,
    internal: QuerySet[Assessment] | None = None,
    user: HAWCUser | None = None,
) -> QuerySet[Study]:
    filters = Q()

    if all_public or public:
        filters1 = dict(
            full_citation__icontains=query,
            published=True,
            assessment__public_on__isnull=False,
            assessment__hide_from_public_page=False,
        )
        if not all_public and public:
            filters1.update(assessment__in=public)
        filters |= Q(**filters1)

    if user and (all_internal or internal):
        internal_assessments = Assessment.objects.all().user_can_view(user)
        if not all_internal and internal:
            internal_assessments = internal_assessments.filter(id__in=internal)
        filters2 = dict(
            full_citation__icontains=query,
            assessment__in=internal_assessments,
        )
        filters |= Q(**filters2)

    if not bool(filters):
        return Study.objects.none()

    return Study.objects.filter(filters)


def search_visuals(
    model_cls: ModelBase,
    query: str,
    all_public: bool = False,
    public: QuerySet[Assessment] | None = None,
    all_internal: bool = False,
    internal: QuerySet[Assessment] | None = None,
    user: HAWCUser | None = None,
) -> QuerySet:
    filters = Q()

    ct = ContentType.objects.get_for_model(model_cls)

    if all_public or public:
        filters1 = dict(
            published=True,
            assessment__public_on__isnull=False,
            assessment__hide_from_public_page=False,
        )
        published_labeled_items = LabeledItem.objects.filter(
            label__in=Label.objects.filter(name__icontains=query, published=True), content_type=ct
        ).values_list("object_id", flat=True)
        if not all_public and public:
            filters1.update(assessment__in=public)
        filters |= (Q(title__icontains=query) | Q(id__in=published_labeled_items)) & Q(**filters1)

    if user and (all_internal or internal):
        internal_assessments = Assessment.objects.all().user_can_view(user)
        if not all_internal and internal:
            internal_assessments = internal_assessments.filter(id__in=internal)
        filters2 = dict(
            assessment__in=internal_assessments,
        )
        labeled_items = LabeledItem.objects.filter(
            label__in=Label.objects.filter(name__icontains=query), content_type=ct
        ).values_list("object_id", flat=True)
        filters |= (Q(title__icontains=query) | Q(id__in=labeled_items)) & Q(**filters2)

    if not bool(filters):
        return model_cls.objects.none()

    return model_cls.objects.filter(filters)
