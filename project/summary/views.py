import json

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic.edit import CreateView

from assessment.models import Assessment
from utils.helper import HAWCDjangoJSONEncoder, HAWCdocx
from utils.views import BaseList, BaseCreate, BaseDetail

from . import forms
from . import models


class SummaryTextJSON(BaseDetail):
    model = models.SummaryText

    def dispatch(self, *args, **kwargs):
        self.assessment = get_object_or_404(Assessment, pk=kwargs.get('pk'))
        self.permission_check_user_can_view()
        return super(SummaryTextJSON, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        content = self.model.get_all_tags(self.assessment, json_encode=True)
        return HttpResponse(content, content_type="application/json")


class SummaryTextList(BaseList):
    parent_model = Assessment
    model = models.SummaryText

    def get_queryset(self):
        rt = self.model.get_assessment_root_node(assessment=self.assessment)
        return self.model.objects.filter(pk__in=[rt.pk])


class SummaryReport(SummaryTextList):

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        report = HAWCdocx()
        self.model.build_report(report, self.assessment)
        return report.django_response()


class SummaryTextModify(BaseCreate):
    # handles Create, Update, Delete for Summary Text
    parent_model = Assessment
    parent_template_name = 'assessment'
    model = models.SummaryText
    form_class = forms.SummaryTextForm

    def post(self, request, *args, **kwargs):
        status = "fail"
        result = []
        if request.is_ajax() and request.user.is_authenticated():
            try:
                post = self.request.POST.copy()
                post.pop('csrfmiddlewaretoken')
                post.pop('_wysihtml5_mode', None)
                post['assessment'] = self.assessment
                existing_id = int(post.pop(u'id', -1)[0])
                delete = post.pop(u'delete', [False])[0]

                if int(post.get('sibling', -1))>0:
                    post['sibling'] = get_object_or_404(self.model, pk=post['sibling'])
                    post.pop('parent')
                else:
                    post.pop('sibling')

                if int(post.get('parent', -1))>0:
                    post['parent'] = get_object_or_404(self.model, pk=post['parent'])
                else:
                    post.pop('parent', None)

                if existing_id>0:
                    obj = get_object_or_404(self.model, pk=existing_id)
                    if delete:
                        obj.delete()
                    else:
                        if obj.assessment != self.assessment:
                            raise Exception("Selected object is not from the same assessment")
                        obj.modify(**post)
                else:
                    self.model.add_summarytext(**post)

                status = "ok"
                result = self.model.get_all_tags(self.assessment, json_encode=False)
            except Exception as e:
                result.append(unicode(e))

        response = {"status": status, "content": result}
        return HttpResponse(json.dumps(response, cls=HAWCDjangoJSONEncoder),
                            content_type="application/json")
