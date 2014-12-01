from rest_framework import serializers
from rest_framework.exceptions import ParseError

from . import models


class IdentifiersSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source='get_url', read_only=True)

    def transform_database(self, obj, value):
        return obj.get_database_display()

    class Meta:
        model = models.Identifiers


class ReferenceTagsSerializer(serializers.WritableField):
    # http://blog.pedesen.de/2013/07/06/Using-django-rest-framework-with-tagged-items-django-taggit/

    def from_native(self, data):
        raise ParseError("Write-not implemented")

    def to_native(self, obj):
        if type(obj) is not list:
            return [{"id": tag.id, "name": tag.name} for tag in obj.all()]
        return obj

