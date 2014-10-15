import json

from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import slugify
from django.views.generic import ListView
from django.views.generic.edit import CreateView, DeleteView

from assessment.models import Assessment
from utils.helper import HAWCDjangoJSONEncoder, HAWCdocx
from utils.views import AssessmentPermissionsMixin, MessageMixin, BaseDetail, BaseUpdate, BaseList

from . import forms
from . import models


class CommentSettingsDetail(BaseDetail):
    model = models.CommentSettings


class CommentSettingsUpdate(BaseUpdate):
    model = models.CommentSettings
    form_class = forms.CommentSettingsForm
    success_message = 'Comment settings updated.'


class CommentList(AssessmentPermissionsMixin, ListView):
    model = models.Comment

    def get_queryset(self):
        if self.kwargs['content_type'] == "assessment_all":
            self.assessment = get_object_or_404(Assessment, pk=self.kwargs['object_id'])
            return models.Comment.objects.filter(assessment=self.assessment)
        else:
            ct = models.Comment.get_content_object_type(self.kwargs['content_type'])
            return models.Comment.objects.filter(content_type=ct,
                                                 object_id=self.kwargs['object_id'])

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        content = "[]"

        if (self.object_list.count() > 0):
            self.assessment = self.object_list[0].content_object.get_assessment()
            self.permission_check_user_can_view()
            content = models.Comment.get_jsons(self.object_list)
        return HttpResponse(content, content_type="application/json")


class CommentCreate(CreateView):
    model = models.Comment
    form_class = forms.CommentForm

    def get(self, request, *args, **kwargs):
        raise Http404

    def get_form_kwargs(self):
        kwargs = super(CreateView, self).get_form_kwargs()
        kwargs['object_id'] = self.kwargs['object_id']
        kwargs['content_type'] = self.kwargs['content_type']
        kwargs['commenter'] = self.request.user
        kwargs['slug'] = slugify(self.request.POST.get('title', ''))
        return kwargs

    def post(self, request, *args, **kwargs):
        response = {"status": "fail",
                    "object": None,
                    "details": ""}
        try:
            self.object = None
            form_class = self.get_form_class()
            form = self.get_form(form_class)

            if form.is_valid():
                form.save()
                response["status"] = "success"
                response["object"] = form.instance.get_json(json_encode=False)
            else:
                response['details'] = dict(form.errors.items())
        except Exception as e:
            response['details'] = unicode(e)

        return HttpResponse(json.dumps(response, cls=HAWCDjangoJSONEncoder),
                                content_type="application/json")


class CommentDelete(DeleteView):
    model = models.Comment

    def get(self, request, *args, **kwargs):
        raise Http404

    def delete(self, request, *args, **kwargs):
        response = {"status": "failed"}
        self.object = self.get_object()
        if self.object.commenter == self.request.user:
            self.object.delete()
            response["status"] = "success"

        return HttpResponse(json.dumps(response, cls=HAWCDjangoJSONEncoder),
                                content_type="application/json")


class CommentListAssessment(BaseList):
    parent_model = Assessment
    model = models.Comment

    def get_queryset(self):
        return self.model.objects.filter(assessment=self.assessment)


class CommentReport(CommentListAssessment):

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        report = HAWCdocx()
        models.Comment.docx_print_report(report, self.assessment, self.object_list)
        return report.django_response()
