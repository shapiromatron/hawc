from typing import Any

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic.types import PositiveInt

from ..lit.models import Reference
from . import models


class ModifyTagUDFContent(BaseModel):
    assessment: int
    reference: PositiveInt
    tag_binding: PositiveInt
    content: dict

    reference_obj: Any = Field(None)
    tag_binding_obj: Any = Field(None)

    @model_validator(mode="after")
    def check_objects(self):
        # get a tag binding for this assessment
        try:
            self.tag_binding_obj = models.TagBinding.objects.assessment_qs(self.assessment).get(
                id=self.tag_binding
            )
        except ObjectDoesNotExist as err:
            raise ValueError("Tag binding not found") from err

        # get a reference for this assessment
        try:
            self.reference_obj = Reference.objects.assessment_qs(self.assessment).get(
                id=self.reference
            )
        except ObjectDoesNotExist as err:
            raise ValueError("Reference not found") from err

        # check that UDF content conforms to schema
        self.tag_binding_obj.form.validate_data(self.content)

        return self


class ModifyModelUDFContent(BaseModel):
    assessment: int
    content_type: str
    object_id: PositiveInt
    content: dict

    content_type_obj: Any = Field(None)
    obj: Any = Field(None)
    binding_obj: Any = Field(None)

    @field_validator("content_type")
    @classmethod
    def ct_format(cls, v: str) -> str:
        if len(v.split(".")) != 2:
            raise ValueError("Must provide a content_type in the form {app_label}.{model}")
        return v

    @model_validator(mode="after")
    def check_objects(self):
        # get a valid content type
        ct = self.content_type.split(".")
        try:
            self.content_type_obj = ContentType.objects.get(app_label=ct[0], model=ct[1])
        except ObjectDoesNotExist as err:
            raise ValueError("Content type not found") from err

        # get an object for this assessment and content type
        try:
            self.obj = (
                self.content_type_obj.model_class()
                .objects.assessment_qs(self.assessment)
                .get(id=self.object_id)
            )
        except ObjectDoesNotExist as err:
            raise ValueError("Object not found") from err

        # get a model binding for this assessment for this content type
        try:
            self.binding_obj = models.ModelBinding.objects.assessment_qs(self.assessment).get(
                content_type=self.content_type_obj
            )
        except ObjectDoesNotExist as err:
            raise ValueError(
                "Model binding not found for this content type and assessment"
            ) from err

        # check that UDF content conforms to schema
        self.binding_obj.form.validate_data(self.content)

        return self
