from json import dumps, loads
import logging

from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import HttpResponse, get_object_or_404
from django.views.generic import TemplateView
from django.views.generic.edit import UpdateView

from assessment.models import Assessment
from animal.models import Endpoint, DoseUnits
from utils.views import (BaseCreate, BaseUpdate, BaseDetail)

from bmds.bmds import BMDS
from . import forms
from . import models


class BMDRead(BaseDetail):
    model = models.BMD_session

    def get_object(self, **kwargs):
        # return latest version of a BMD session; else throw 404
        try:
            obj = self.model.objects.filter(endpoint=self.kwargs.get('pk')).latest()
        except:
            raise Http404
        return super(BMDRead, self).get_object(object=obj)

    def get_context_data(self, **kwargs):
        context = super(BMDRead, self).get_context_data(**kwargs)
        context['endpoint_json'] = self.object.endpoint.d_response(json_encode=True, dose_pk=self.object.dose_units.pk)
        context['session'] = self.object.webpage_return(json=True)
        logics = models.LogicField.objects.filter(assessment=self.assessment)
        context['logics'] = models.LogicField.website_list_return(logics, self.object.endpoint.data_type, True)
        context['bmds_version'] = self.assessment.BMD_Settings.BMDS_version
        return context


class BMDCreate(BaseCreate):
    """
    Execute a BMD_session in POST and save if successful. If not successful,
    delete the temporary BMD_session that was created. Note that this view may
    also view an existing BMD session with the possibility to select a new
    selected model, without creating a new BMD_session.
    """
    success_message = 'BMD modeling session created.'
    parent_model = Endpoint
    parent_template_name = 'endpoint'
    model = models.BMD_session
    form_class = forms.BMD_SessionForm

    def post(self, request, *args, **kwargs):
        model_settings = loads(request.body)  # json
        units = get_object_or_404(DoseUnits, pk=model_settings.get('dose_units_id'))
        logging.debug('saving new session')
        session = models.BMD_session(endpoint=self.parent,
                                     BMDS_version=self.assessment.BMD_Settings.BMDS_version,
                                     bmrs=dumps(model_settings.get('bmrs')),
                                     dose_units=units)

        session.save()  # initial save so foreign keys can link
        logging.debug('running session')
        try:
            session.run_session(self.parent, model_settings)
            output = session.webpage_return(json=True)
        except Exception as e:
            output = {'error': e.message}

        return HttpResponse(dumps(output), content_type="application/json")

    def get_context_data(self, **kwargs):
        context = super(BMDCreate, self).get_context_data(**kwargs)
        # add existing BMD_session if present
        try:
            existing = self.model.objects.filter(endpoint=self.parent).latest()
            context['crud'] = "Edit"  # todo: change to "Update", require JS updates
            context['session'] = existing.webpage_return(json=True)
        except:
            existing = None
            context['template'] = models.BMD_session.get_template(self.assessment,
                                                                  self.parent.data_type,
                                                                  json=True)
        context['object'] = existing
        logics = self.assessment.BMD_Logic_Fields.all()
        context['logics'] = models.LogicField.website_list_return(logics, self.parent.data_type, True)
        context['bmds_version'] = self.assessment.BMD_Settings.BMDS_version
        return context


class BMDVersions(BMDRead):
    template_name = "bmd/bmd_session_versions.html"
    crud = 'Update'  # requires edit-level permissions to view

    def get_context_data(self, **kwargs):
        context = super(BMDVersions, self).get_context_data(**kwargs)
        context['endpoint'] = self.object.endpoint
        context['object_list'] = self.model.objects.filter(endpoint=self.kwargs.get('pk')).order_by('last_updated')
        return context


class BMDSelectionUpdate(BaseUpdate):
    success_message = 'BMD selection updated.'
    model = models.BMD_session
    http_method_names = (u'post', )  # don't allow GET

    def get_success_url(self):
        return self.object.endpoint.get_absolute_url()

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.process_data()
        return HttpResponseRedirect(self.get_success_url())

    def process_data(self):
        data = loads(self.request.body)
        model_run = models.BMD_model_run.objects.filter(pk=data.get('model')).first()
        self.object.notes = data.get('notes')
        self.object.selected_model = model_run
        self.object.save()
        for run_data in data.get('overrides'):
            models.BMD_model_run.objects.filter(pk=run_data.get('id'))\
                                .update(override=run_data.get('override'),
                                        override_text=run_data.get('override_text'))


class getEndpointTemplate(BaseDetail):
    """
    Get a clean model-template to be used for model-configuration. This is not
    usually needed unless a user presses the "reset" template button.
    """
    model = Endpoint

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        data = models.BMD_session.get_template(self.assessment,
                                               self.object.data_type,
                                               json=True)
        return HttpResponse(data, content_type="application/json")


class getDefaultOptions(TemplateView):
    """
    Return json object for the default model options for a given model_type and
    BMDS version.
    """
    def get(self, request, *args, **kwargs):
        try:
            version = BMDS.versions[str(self.kwargs['vbmds'])]
            data = {
                'options': version.models[self.kwargs['datatype']].keys(),
                'bmrs': version.bmrs[self.kwargs['datatype']]
            }
        except:
            data = {'error': 'No BMDS models meet this description.'}
        return HttpResponse(dumps(data), content_type="application/json")


class getSingleModelOption(TemplateView):
    """
    Return json object for the default model options for a given model_type and
    BMDS version.
    """
    def get(self, request, *args, **kwargs):
        try:
            version = BMDS.versions[str(self.kwargs['vbmds'])]
            run_instance = version.models[self.kwargs['datatype']][self.kwargs['model_name']]()
            model_data = models.BMD_model_run.get_model_template(self.kwargs['model_name'], run_instance)
        except:
            model_data = {'error': 'No BMDS models meet this description.'}
        return HttpResponse(dumps(model_data), content_type="application/json")


class AssessSettingsRead(BaseDetail):
    model = models.BMD_Assessment_Settings

    def get_object(self, **kwargs):
        self.assessment = get_object_or_404(Assessment, pk=self.kwargs.get('pk'))
        obj = self.assessment.BMD_Settings
        return super(AssessSettingsRead, self).get_object(object=obj)


class AssessSettingsUpdate(BaseUpdate):
    # settings can only be changed by project-managers
    success_message = 'BMD Settings updated.'
    model = models.BMD_Assessment_Settings
    form_class = forms.AssessmentSettingsForm

    def get_object(self, **kwargs):
        obj = super(AssessSettingsUpdate, self).get_object()
        if not self.assessment.user_can_edit_assessment(self.request.user):
            raise PermissionDenied
        return obj


class AssessLogicUpdate(BaseUpdate):
    success_message = 'BMD Logic Settings updated.'
    model = models.LogicField
    form_class = forms.LogicFieldForm

    def get_success_url(self):
        return reverse_lazy('bmd:assess_settings_detail', kwargs={'pk': self.object.assessment.pk})
