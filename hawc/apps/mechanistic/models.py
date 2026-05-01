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

    # experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE, related_name="chemicals")
    study = models.ForeignKey(Study, on_delete=models.CASCADE, related_name="mechanistic_chemicals")
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

    BREADCRUMB_PARENT = "study"

    TEXT_CLEANUP_FIELDS = ("name","cas","source","comments")

    class Meta:
        ordering = ("id",)

    def get_assessment(self):
        # return self.experiment.get_assessment()
        return self.study.get_assessment()

    def get_study(self):
        # return self.experiment.get_study()
        return self.study

    def get_absolute_url(self):
        return reverse("mechanistic:chemical_detail", args=(self.pk,))

    def get_update_url(self):
        return reverse("mechanistic:chemical_update", args=(self.pk,))

    def get_delete_url(self):
        return reverse("mechanistic:chemical_delete", args=(self.pk,))

    def __str__(self):
        return self.name

    def clone(self):
        self.id = None
        self.name = clone_name(self, "name")
        self.save()
        return self


class TestSystem(models.Model):
    objects = managers.TestSystemManager()

    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE, related_name="testsystems")
    name = models.CharField(
        max_length=255,
        help_text="Provide a descriptive name for the experiment (e.g. Estrogen Receptor Biding Assay Using Rat Uterine Cytosol)",
    )
    test_system_type = models.CharField(
        blank=True,
        max_length=3,
        choices=constants.TestSystemType,
        help_text="A test system is any biological, chemical or physical system or a combination thereof used in a study (OECD (2018), Guidance Document on Good In Vitro Method Practices (GIVIMP), OECD Series on Testing and Assessment, No. 286, OECD Publishing, Paris).<p>Examples of physical chemical based test systems: serum protein, peptide, enzyme.<p>Select complex biological test system for example in case of: 3D model, induced pluripotent stem cells, organ on a chip, co-cultures, etc.<p>Select 'other:' in case you don't find a suitable option, for example when your test system is a test kit or a lower in vivo organism.<p>If select “other” enter in free text field “Type of test system “other” remarks”"
    )
    test_system_type_other = models.CharField(
        max_length=255, help_text="Specify the type of test system", blank=True
    )
    description = models.CharField(
        max_length=255, help_text="Describe the composition of the test system, e.g. the cells / tissues / proteins / 3D models / induced pluripotent stem cells / organ on chip / co-cultures etc. that were used in the study. When applicable, provide the following information on the genetic modification: - Gene inserted - Gene species (e.g. human, rat, mouse) - Additional information on modification", blank=True
    )
    species = models.ForeignKey("assessment.Species", on_delete=models.CASCADE, blank=True, default=None)
    supplier = models.CharField(
        blank=True,
        max_length=2,
        verbose_name="Source/Supplier",
        choices=constants.TestSystemSupplier,
        help_text="Select the appropriate test system used in the experiment.<p>In case the test system needs to be created in house (e.g. co-cultures, genetic modification), select 'in house developed'"
    )
    supplier_remarks = models.CharField(
        blank=True,
        max_length=255,
        verbose_name="Source/Supplier Remarks",
        help_text="Provide information on the test system source and select if the test system was obtained from a commercial (e.g. cell bank) or non-commercial supplier (e.g. collaborating organisation), or if it was in-house developed or established."
    )
    catalogue_number = models.CharField(
        blank=True,
        max_length=255,
        help_text="Provide the following details for the test system:<br><ul><li>Name</li><li>Source / supplier</li><li>Catalogue / batch number</li><ul>"
    )
    batch_number = models.CharField(
        verbose_name="Lot/Batch Number",
        blank=True,
        max_length=255,
        help_text="Provide the batch/lot number that was used in the study. If unknown, enter “unknown”."
    )
    genetic_modification = models.CharField(
        verbose_name="Genetic modification of the test system",
        max_length=12,
        choices=constants.GeneticModification,
        help_text="Help text: Select option that best fits - if genetically modified after purchase, prior to use or genetically modified by supplier add additional information on modification in remarks field"
    )
    genetic_modification_remarks = models.CharField(
        blank=True,
        max_length=255,
        verbose_name="Genetic modification of the test system remarks",
        help_text="When applicable, provide the following information on the genetic modification:<ul><li>Gene inserted</li><li>Gene species (e.g. human, rat, mouse)</li></ul>"
    )
    metabolic_competence = models.CharField(
        verbose_name="Metabolic competence of the test system",
        max_length=3,
        choices=constants.MetabolicCompetence,
        help_text="Select the option that fits best and describe the knowledge about the metabolic competence (i.e. Phase I and/or II biotransformation capacity) of the test system under remarks.<p>For example, when the test system used is  cryopreserved human pooled liver tissue homogenate 9000 g fraction (S9) procured from a commercial supplier, select “metabolic activity, specify” and specify: contains phase I and II metabolic enzymes present in the microsomal (e.g. cytochrome P450s, Flavin-containing monooxygenase, uridine 5’-diphospho-glucuronosyltransferases, carboxylesterases) and cytosolic (e.g. sulfotransferases, glutathione S-transferases, methyltransferases, N-acetyl transferases, xanthine oxidase, aldehyde oxidase) fractions."
    )
    metabolic_competence_remarks = models.CharField(
        blank=True,
        max_length=255,
        verbose_name="Metabolic competence of the test system remarks",
        help_text="Describe the method underlying metabolic competence of the test system"
    )
    medium_buffer = models.CharField(
        blank=True,
        max_length=255,
        verbose_name="Stock medium/buffer",
        help_text="Description of stock medium or buffer including name, source, Lot/batch #, pH (if applicable)"
    )
    serum_supplements = models.CharField(
        blank=True,
        max_length=255,
        verbose_name="Stock medium serum/supplements",
        help_text="Describe Serum - name, source, lot/batch #, final conc<p>Supplements - name, source, lot/batch #, final conc"
    )
    maintenance = models.CharField(
        blank=True,
        max_length=255,
        help_text="Provide information on the routine maintenance of the test system: cell-based: Incubation conditions (humidity, temperature, CO2, etc.) Cell-free: buffer, PH, concentration"
    )
    qc_confirmation = models.CharField(
        verbose_name="Confirmation of quality control",
        max_length=9,
        choices=constants.TestSystemQualityControl,
        help_text="Select which quality control that was performed on the test system, before or during the generation of results, to confirm the test system was healthy, stable and responsive. If “other” is selected, please specify in the “confirmation of quality control remarks” field"
    )
    qc_confirmation_remarks = models.CharField(
        blank=True,
        max_length=255,
        help_text="Specify the quality control that was performed on the test system, before or during the generation of results, to confirm the test system was healthy, stable and / or responsive."
    )
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    # BREADCRUMB_PARENT = "study"

    TEXT_CLEANUP_FIELDS = ("name")

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
reversion.register(TestSystem)
