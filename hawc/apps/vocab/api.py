from typing import Optional

from django.db.models import QuerySet
from rest_framework import exceptions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from ..common.helper import tryParseInt
from . import models, serializers


class EhvTermViewset(viewsets.GenericViewSet):
    serializer_class = serializers.TermSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> QuerySet:
        return models.Term.objects.filter(
            namespace=models.VocabularyNamespace.EHV, deprecated_on__isnull=True
        )

    def filter_qs(self, request: Request, type: models.VocabularyTermType) -> QuerySet:
        term: Optional[str] = request.query_params.get("term")
        parent: Optional[int] = tryParseInt(request.query_params.get("parent"))
        limit: Optional[int] = tryParseInt(request.query_params.get("limit"), 100, 1, 10000)
        qs = self.get_queryset().filter(type=type)
        if term:
            qs = qs.filter(name__icontains=term)
        if parent:
            qs = qs.filter(parent=parent)
        return qs[:limit]

    @action(detail=False)
    def system(self, request: Request) -> Response:
        qs = self.filter_qs(request, models.VocabularyTermType.system)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False)
    def organ(self, request: Request) -> Response:
        qs = self.filter_qs(request, models.VocabularyTermType.organ)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False)
    def effect(self, request: Request) -> Response:
        qs = self.filter_qs(request, models.VocabularyTermType.effect)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False)
    def effect_subtype(self, request: Request) -> Response:
        qs = self.filter_qs(request, models.VocabularyTermType.effect_subtype)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False)
    def endpoint_name(self, request: Request) -> Response:
        qs = self.filter_qs(request, models.VocabularyTermType.endpoint_name)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, url_path="endpoint-name-lookup")
    def endpoint_name_lookup(self, request: Request, pk: int) -> Response:
        try:
            term = models.Term.objects.get(
                id=pk,
                type=models.VocabularyTermType.endpoint_name,
                namespace=models.VocabularyNamespace.EHV,
                deprecated_on__isnull=True,
            )
        except models.Term.DoesNotExist:
            raise exceptions.NotFound()
        return Response(term.ehv_endpoint_name())

    @action(detail=True, methods=("post",), url_path="related-entity")
    def related_entity(self, request: Request, pk: int = None) -> Response:
        term = self.get_object()
        entity_serializer = serializers.EntitySerializer(data=request.data)
        entity_serializer.is_valid(raise_exception=True)
        entity, _ = models.Entity.objects.get_or_create(**entity_serializer.validated_data)
        entity.terms.add(term, through_defaults={"notes": request.data.get("notes", "")})
        serializer = self.get_serializer(entity.terms.all(), many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
