from django.test import TestCase


class FormTester(TestCase):

    def createTestForm(self, inps, *args, **kwargs):
        """
        Should return an form instance for testing
        """
        raise NotImplementedError("Requries override.")

    def fieldHasError(self, inps, field, msg, *args, **kwargs):
        form = self.createTestForm(inps, *args, **kwargs)
        form.full_clean()
        self.assertTrue(msg in form.errors[field])
