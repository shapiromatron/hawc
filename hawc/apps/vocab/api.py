from django.db import transaction
from django.db.models import QuerySet
from rest_framework import exceptions, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from ..common.helper import FlatExport, tryParseInt
from ..common.renderers import PandasRenderers
from . import constants, models, serializers


class EhvTermViewSet(viewsets.GenericViewSet):
    serializer_class = serializers.SimpleTermSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> QuerySet:
        return models.Term.objects.filter(
            namespace=constants.VocabularyNamespace.EHV, deprecated_on__isnull=True
        )

    def filter_qs(self, request: Request, type: constants.VocabularyTermType) -> QuerySet:
        term: str | None = request.query_params.get("term")
        parent: int | None = tryParseInt(request.query_params.get("parent"))
        limit: int | None = tryParseInt(request.query_params.get("limit"), 100, 1, 10000)
        qs = self.get_queryset().filter(type=type)
        if term:
            qs = qs.filter(name__icontains=term)
        if parent:
            qs = qs.filter(parent=parent)
        return qs[:limit]

    @action(detail=False, renderer_classes=PandasRenderers)
    def nested(self, request: Request):
        df = models.Term.ehv_dataframe()
        return FlatExport.api_response(df=df, filename="ehv")

    @action(detail=False)
    def system(self, request: Request) -> Response:
        qs = self.filter_qs(request, constants.VocabularyTermType.system)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False)
    def organ(self, request: Request) -> Response:
        qs = self.filter_qs(request, constants.VocabularyTermType.organ)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False)
    def effect(self, request: Request) -> Response:
        qs = self.filter_qs(request, constants.VocabularyTermType.effect)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False)
    def effect_subtype(self, request: Request) -> Response:
        qs = self.filter_qs(request, constants.VocabularyTermType.effect_subtype)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False)
    def endpoint_name(self, request: Request) -> Response:
        qs = self.filter_qs(request, constants.VocabularyTermType.endpoint_name)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, url_path="endpoint-name-lookup")
    def endpoint_name_lookup(self, request: Request, pk: int) -> Response:
        try:
            term = models.Term.objects.get(
                id=pk,
                type=constants.VocabularyTermType.endpoint_name,
                namespace=constants.VocabularyNamespace.EHV,
                deprecated_on__isnull=True,
            )
        except models.Term.DoesNotExist:
            raise exceptions.NotFound()
        return Response(term.ehv_endpoint_name())

    @action(detail=True, methods=("post",), url_path="related-entity")
    def related_entity(self, request: Request, pk: int | None = None) -> Response:
        term = self.get_object()
        entity_serializer = serializers.EntitySerializer(data=request.data)
        entity_serializer.is_valid(raise_exception=True)
        entity, _ = models.Entity.objects.get_or_create(**entity_serializer.validated_data)
        entity.terms.add(term, through_defaults={"notes": request.data.get("notes", "")})
        serializer = self.get_serializer(entity.terms.all(), many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TermViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = serializers.TermSerializer
    queryset = models.Term.objects.all()

    @transaction.atomic
    @action(
        detail=False, methods=("post",), permission_classes=(IsAdminUser,), url_path="bulk-create"
    )
    def bulk_create(self, request: Request) -> Response:
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @transaction.atomic
    @action(
        detail=False, methods=("patch",), permission_classes=(IsAdminUser,), url_path="bulk-update"
    )
    def bulk_update(self, request: Request) -> Response:
        qs = self.get_queryset().filter(id__in=[obj_data.get("id") for obj_data in request.data])
        serializer = self.get_serializer(instance=qs, data=request.data, many=True, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def uids(self, request: Request) -> Response:
        qs = self.get_queryset().exclude(uid=None)
        return Response(qs.values_list("id", "uid"))
