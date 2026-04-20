import reversion
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse

from ..assessment.models import DSSTox
from ..common.models import clone_name
from ..study.models import Study
from . import constants, managers


class Experiment(models.Model):
    objects = managers.ExperimentManager()

    study = models.ForeignKey(Study, on_delete=models.CASCADE, related_name="mechanistic_experiments")

    name = models.CharField(
        verbose_name="Method Name",
        help_text="Name / identifier of the method (if available)",
        max_length=255,
    )
    description = models.TextField(
        verbose_name="Method Description",
        help_text="Provide a short description of the method and how it is relevant to the endpoint being investigated.",
        blank=True
    )

    protocol = models.FileField(upload_to = "mechanistic-experiment-protocols", blank=True, help_text="In case the protocol is available (e.g. as supplement to a publication), please provide it as an attachment. The protocol includes the practical steps that were performed in the laboratory to generate the data.")

    test_facility = models.TextField(
        help_text="If available, enter: Test Facility Name, Location, Study director name, Other personnel name and responsibility, Study period: study start and end dates",
        blank=True
    )

    guideline = models.CharField(
        max_length=3,
        choices=constants.ExperimentGuideline,
        help_text="Select whether a guideline study was conducted. If yes, enter the TG# in the Guideline Name & Number field"
    )

    guideline_name_number = models.CharField(
        max_length=255,
        verbose_name = "Guideline Name & Number",
        help_text="Enter in Guideline; e.g. OECD or OCSPP"
    )

    guideline_compliance = models.CharField(blank=True)

    # BE SURE TO UPDATE views.py's prepopulation if you add new fields!!!

    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    BREADCRUMB_PARENT = "study"

    TEXT_CLEANUP_FIELDS = (
        "name",
        "comments",
    )

    class Meta:
        verbose_name = "Mechanistic Experiment"
        verbose_name_plural = "Mechanistic Experiments"
        ordering = ("id",)

    def get_assessment(self):
        return self.study.get_assessment()

    def get_study(self):
        return self.study

    def get_absolute_url(self):
        return reverse("mechanistic:experiment_detail", args=(self.pk,))

    def get_update_url(self):
        return reverse("mechanistic:experiment_update", args=(self.pk,))

    def get_delete_url(self):
        return reverse("mechanistic:experiment_delete", args=(self.pk,))

    def __str__(self):
        return f"{self.name}"


class Chemical(models.Model):
    objects = managers.ChemicalManager()

    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE, related_name="chemicals")
    name = models.CharField(
        max_length=128,
        help_text="This field is commonly used in visualizations, so consider using a common acronym, e.g., BPA instead of Bisphenol A",
    )
    dsstox = models.ForeignKey(
        DSSTox,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name="DSSTox substance identifier",
        help_text=DSSTox.help_text(),
        related_name="mechanistic_dsstox",
    )
    cas = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Chemical identifier (CAS)",
        help_text="CAS #",
    )

    source = models.CharField(
        max_length=255, help_text="Company and catalog number (if available)", blank=True
    )

    composition_purity = models.CharField(
        max_length=2,
        choices=constants.CompositionPurity,
        verbose_name="Composition / Purity",
        help_text="If detailed information on the purity of the composition is not known, a qualitative statement can be provided in this field, e.g. 'analytical grade' or 'technical grade'. A chemical can be created for a mixture/product. If the chemical refers to the composition of the mixture/product, in the field % purity, specify the chemical composition."
    )

    composition_purity_other = models.CharField(
        max_length=255, help_text="Enter additional details about composition/purity.", blank=True
    )

    percent_purity = models.FloatField(
        blank=True,
        null=True,
        verbose_name="% Purity",
        help_text="Provide the % purity or chemical composition",
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    comments = models.TextField(
        blank=True,
        verbose_name="Chemical description comment",
        help_text="Enter other descriptive information on the chemical, e.g. technical, nature, relevant P-chem properties.",
    )
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    TEXT_CLEANUP_FIELDS = ("name","cas","source","comments")

    class Meta:
        ordering = ("id",)

    def get_assessment(self):
        return self.experiment.get_assessment()

    def get_study(self):
        return self.experiment.get_study()

    def __str__(self):
        return self.name

    def clone(self):
        self.id = None
        self.name = clone_name(self, "name")
        self.save()
        return self


reversion.register(Experiment)
reversion.register(Chemical)
