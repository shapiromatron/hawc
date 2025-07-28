from django.views.debug import ExceptionReporter as BaseExceptionReporter


class AssessmentNotFound(Exception):
    """Raise when an assessment cannot be determined"""

    pass


class ExceptionReporter(BaseExceptionReporter):
    """Remove django settings from report"""

    def get_traceback_data(self):
        context = super().get_traceback_data()
        context["settings"] = {"values": "removed from report"}
        return context
