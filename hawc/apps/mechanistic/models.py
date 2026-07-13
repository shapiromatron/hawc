import json, reversion

from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator, MinValueValidator
from django import forms
from django.db import models
from django.forms import ModelForm
from django.urls import reverse

from ..assessment.models import Assessment, BaseEndpoint, DSSTox
from ..common.models import JSONListField, NumericTextField, clone_name
from ..study.models import Study
from ..vocab.constants import VocabularyNamespace
from ..vocab.models import Term
from . import constants, managers


class Experiment(models.Model):
    objects = managers.ExperimentManager()

    study = models.ForeignKey(
        Study, on_delete=models.CASCADE, related_name="mechanistic_experiments"
    )

    name = models.CharField(
        verbose_name="Method Name",
        help_text="Name / identifier of the method (if available)",
        max_length=255,
    )
    has_high_throughput = models.BooleanField(
        verbose_name="High throughput?",
        help_text="Indicate if the experiment is high throughput.",
        default=False,
    )
    description = models.TextField(
        verbose_name="Method Description",
        help_text="Provide a short description of the method and how it is relevant to the endpoint being investigated.",
        blank=True,
    )

    protocol = models.FileField(
        upload_to="mechanistic-experiment-protocols",
        blank=True,
        help_text="In case the protocol is available (e.g. as supplement to a publication), please provide it as an attachment. The protocol includes the practical steps that were performed in the laboratory to generate the data.",
    )

    test_facility = models.TextField(
        help_text="If available, enter:<br><ul><li>Test Facility Name</li><li>Location</li><li>Study director name</li><li>Other personnel name and responsibility</li><li>Study period: study start and end dates</li></ul>",
        blank=True,
    )

    guideline = models.CharField(
        max_length=3,
        choices=constants.ExperimentGuideline,
        help_text="Select whether a guideline study was conducted. If yes, enter the TG# in the Guideline Name & Number field",
    )

    guideline_name_number = models.CharField(
        max_length=255,
        verbose_name="Guideline Name & Number",
        help_text="Enter in Guideline; e.g. OECD or OCSPP",
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
        help_text="If detailed information on the purity of the composition is not known, a qualitative statement can be provided in this field, e.g. 'analytical grade' or 'technical grade'. A chemical can be created for a mixture/product. If the chemical refers to the composition of the mixture/product, in the field % purity, specify the chemical composition.",
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

    TEXT_CLEANUP_FIELDS = ("name", "cas", "source", "comments")

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
        help_text="A test system is any biological, chemical or physical system or a combination thereof used in a study (OECD (2018), Guidance Document on Good In Vitro Method Practices (GIVIMP), OECD Series on Testing and Assessment, No. 286, OECD Publishing, Paris).<p>Examples of physical chemical based test systems: serum protein, peptide, enzyme.<p>Select complex biological test system for example in case of: 3D model, induced pluripotent stem cells, organ on a chip, co-cultures, etc.<p>Select 'other:' in case you don't find a suitable option, for example when your test system is a test kit or a lower in vivo organism.<p>If select “other” enter in free text field “Type of test system “other” remarks”",
    )
    test_system_type_other = models.CharField(
        max_length=255, help_text="Specify the type of test system", blank=True
    )
    description = models.CharField(
        max_length=255,
        help_text="Describe the composition of the test system, e.g. the cells / tissues / proteins / 3D models / induced pluripotent stem cells / organ on chip / co-cultures etc. that were used in the study. When applicable, provide the following information on the genetic modification: - Gene inserted - Gene species (e.g. human, rat, mouse) - Additional information on modification",
        blank=True,
    )
    species = models.ForeignKey("assessment.Species", on_delete=models.CASCADE)
    supplier = models.CharField(
        blank=True,
        max_length=2,
        verbose_name="Source/Supplier",
        choices=constants.TestSystemSupplier,
        help_text="Select the appropriate test system used in the experiment.<p>In case the test system needs to be created in house (e.g. co-cultures, genetic modification), select 'in house developed'",
    )
    supplier_remarks = models.CharField(
        blank=True,
        max_length=255,
        verbose_name="Source/Supplier Remarks",
        help_text="Provide information on the test system source and select if the test system was obtained from a commercial (e.g. cell bank) or non-commercial supplier (e.g. collaborating organisation), or if it was in-house developed or established.",
    )
    catalogue_number = models.CharField(
        blank=True,
        max_length=255,
        help_text="Provide the following details for the test system:<br><ul><li>Name</li><li>Source / supplier</li><li>Catalogue / batch number</li><ul>",
    )
    batch_number = models.CharField(
        verbose_name="Lot/Batch Number",
        blank=True,
        max_length=255,
        help_text="Provide the batch/lot number that was used in the study. If unknown, enter “unknown”.",
    )
    genetic_modification = models.CharField(
        verbose_name="Genetic modification of the test system",
        max_length=12,
        choices=constants.GeneticModification,
        help_text="Help text: Select option that best fits - if genetically modified after purchase, prior to use or genetically modified by supplier add additional information on modification in remarks field",
    )
    genetic_modification_remarks = models.CharField(
        blank=True,
        max_length=255,
        verbose_name="Genetic modification of the test system remarks",
        help_text="When applicable, provide the following information on the genetic modification:<ul><li>Gene inserted</li><li>Gene species (e.g. human, rat, mouse)</li></ul>",
    )
    metabolic_competence = models.CharField(
        verbose_name="Metabolic competence of the test system",
        max_length=3,
        choices=constants.MetabolicCompetence,
        help_text="Select the option that fits best and describe the knowledge about the metabolic competence (i.e. Phase I and/or II biotransformation capacity) of the test system under remarks.<p>For example, when the test system used is  cryopreserved human pooled liver tissue homogenate 9000 g fraction (S9) procured from a commercial supplier, select “metabolic activity, specify” and specify: contains phase I and II metabolic enzymes present in the microsomal (e.g. cytochrome P450s, Flavin-containing monooxygenase, uridine 5’-diphospho-glucuronosyltransferases, carboxylesterases) and cytosolic (e.g. sulfotransferases, glutathione S-transferases, methyltransferases, N-acetyl transferases, xanthine oxidase, aldehyde oxidase) fractions.",  # noqa: RUF001
    )
    metabolic_competence_remarks = models.CharField(
        blank=True,
        max_length=255,
        verbose_name="Metabolic competence of the test system remarks",
        help_text="Describe the method underlying metabolic competence of the test system",
    )
    medium_buffer = models.CharField(
        blank=True,
        max_length=255,
        verbose_name="Stock medium/buffer",
        help_text="Description of stock medium or buffer including name, source, Lot/batch #, pH (if applicable)",
    )
    serum_supplements = models.CharField(
        blank=True,
        max_length=255,
        verbose_name="Stock medium serum/supplements",
        help_text="Describe Serum - name, source, lot/batch #, final conc<p>Supplements - name, source, lot/batch #, final conc",
    )
    maintenance = models.CharField(
        blank=True,
        max_length=255,
        help_text="Provide information on the routine maintenance of the test system: cell-based: Incubation conditions (humidity, temperature, CO2, etc.) Cell-free: buffer, PH, concentration",
    )
    qc_confirmation = models.CharField(
        verbose_name="Confirmation of quality control",
        max_length=9,
        choices=constants.TestSystemQualityControl,
        help_text="Select which quality control that was performed on the test system, before or during the generation of results, to confirm the test system was healthy, stable and responsive. If “other” is selected, please specify in the “confirmation of quality control remarks” field",
    )
    qc_confirmation_remarks = models.CharField(
        blank=True,
        max_length=255,
        help_text="Specify the quality control that was performed on the test system, before or during the generation of results, to confirm the test system was healthy, stable and / or responsive.",
    )
    controls_used = models.CharField(
        verbose_name="Controls / reference items used",
        help_text='Indicate whether controls / reference substances were used. Enter controls data in the "Controls" block.',
        choices=constants.ControlsUsed,
        max_length=2,
    )
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    # BREADCRUMB_PARENT = "study"

    TEXT_CLEANUP_FIELDS = "name"

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


class Method(models.Model):
    objects = managers.MethodManager()

    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE, related_name="methods")
    test_system = models.ForeignKey(TestSystem, on_delete=models.CASCADE, related_name="methods")

    endpoint_detection_method = models.CharField(
        choices=constants.EndpointDetectionMethod,
        max_length=10,
        help_text="Indicate the readout used endpoint detection. Select a detection method type from the picklist and provide the type of instrument (e.g. HPLC, Spectrophotometer, Flow cytometer) or chose 'other: and specify the type or equipment used / analysis performed.",
    )
    details = models.CharField(
        verbose_name="Details on detection method",
        choices=constants.EndpointDetails,
        max_length=4,
        help_text="Select what type of qualitative method was used and describe the method in the remarks field below.",
    )
    parameters_measured = ArrayField(
        models.CharField(max_length=3, choices=constants.EndpointParameters),
        help_text="Describe the unit or output that was provided by the instrument during the measurement. This is the instrument unit of measure of the raw data.",
    )
    remarks = models.CharField(
        verbose_name="Remarks on detection method",
        help_text="Provide any other relevant information on the detection method not described above",
        blank=True,
    )

    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    TEXT_CLEANUP_FIELDS = "remarks"

    class Meta:
        ordering = ("id",)

    def get_assessment(self):
        return self.experiment.get_assessment()

    def get_study(self):
        return self.experiment.get_study()

    def __str__(self):
        return self.endpoint_detection_method

    def clone(self):
        self.id = None
        # self.name = clone_name(self, "name")
        self.save()
        return self


class TestDesign(models.Model):
    objects = managers.TestDesignManager()

    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE, related_name="testdesigns")
    test_system = models.ForeignKey(
        TestSystem, on_delete=models.CASCADE, related_name="testdesigns"
    )

    vehicle = models.CharField(
        verbose_name="Vehicle/Solvent",
        max_length=4,
        choices=constants.VehicleSolventType,
        help_text="If a vehicle or solvent was used, select the relevant item or use 'other:' and specify.",
    )

    vehicle_other = models.CharField(
        verbose_name="Vehicle/Solvent: Additional Details",
        max_length=255,
        help_text="Enter additional details about vehicle/solvent.",
        blank=True,
    )

    final_concentration_vehicle = models.CharField(
        verbose_name="Final concentration of the vehicle/solvent",
        max_length=4,
        choices=constants.VehicleSolventConcentrationAmount,
        help_text="Specify the % of vehicle / solvent in the final incubation mixture",
        blank=True,
    )

    final_concentration_vehicle_other = models.CharField(
        verbose_name="Final concentration: Additional Details",
        max_length=255,
        help_text="Enter additional details about final concentration.",
        blank=True,
    )

    final_concentration_vehicle_units = models.CharField(
        verbose_name="Final concentration of the vehicle/solvent unit",
        max_length=4,
        choices=constants.VehicleSolventConcentrationUnit,
        help_text="Specify the vehicle / solvent unit",
        blank=True,
    )

    concentration_selection = models.CharField(
        verbose_name="Concentration selection of the test material",
        max_length=4,
        choices=constants.ConcentrationSelection,
        help_text="For data interpretation it is important to know on what basis the highest concentration tested was selected.<p>Any free text explanation can be given in the adjacent text field to justify the dose level selected.",
    )

    # always show it...
    concentration_selection_remarks = models.CharField(
        verbose_name="Concentration selection of the test material: Additional Details",
        help_text="Any free text explanation can be given in the adjacent text field to justify the dose level selected.",
        blank=True,
    )

    concentrations_tested_subfields = [
        {"name": "value", "type": float},
        {"name": "units", "type": str, "choices": constants.ConcentrationUnits},
        {"name": "units_other", "type": str},
    ]
    concentrations_tested = JSONListField(
        blank=True,
        help_text="Concentrations tested",
        sub_fields=concentrations_tested_subfields,  # see above note...maybe lose this and just keep concentrations_tested_subfields, and pass that to the widget.
    )

    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    # BREADCRUMB_PARENT = "study"

    TEXT_CLEANUP_FIELDS = "name"

    class Meta:
        ordering = ("id",)

    def get_assessment(self):
        return self.experiment.get_assessment()

    def get_study(self):
        return self.experiment.get_study()

    def __str__(self):
        return self.get_vehicle_display()

    def clone(self):
        self.id = None
        # self.name = clone_name(self, "name")
        self.save()
        return self


class MechControl(models.Model):
    objects = managers.MechControlManager()

    experiment = models.ForeignKey(
        Experiment, on_delete=models.CASCADE, related_name="mechcontrols"
    )
    test_system = models.ForeignKey(
        TestSystem, on_delete=models.CASCADE, related_name="mechcontrols"
    )

    # note line item 66 -- "controls used" we put this on the test system...

    control_type = models.CharField(
        verbose_name="Type of controls used",
        help_text="Select the type of control used to demonstrate the proper performance of the test system and therefore the validity of the experiments. More than one control/reference item can be provided.<p> Solvent / vehicle controls consist of solvent or vehicle alone, without test material, and otherwise treated in the same way as the treatment groups.<p>Untreated controls consist of culture medium without solvent / vehicle or test material, and otherwise treated in the same way as the treatment groups.<p>True negative controls include items (e.g. chemicals) with known lack of activity.<p>Positive controls include items with known activity.<p>Reference items are substances with known activity, used as basis for comparison with the test material.",
        choices=constants.ControlType,
        max_length=3,
    )
    control_type_other = models.CharField(
        max_length=255, help_text="Enter control type information", blank=True
    )
    description = models.CharField(
        verbose_name="Description of reference and control items used",
        help_text="Describe the reference or control item used or provide the name and identifier (e.g. CAS number), source, lot/batch #, purity, and concentration (range) used.",
        blank=True,
    )
    remarks = models.CharField(
        help_text="Provide any additional information about control and reference items used.",
        blank=True,
    )
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    # BREADCRUMB_PARENT = "study"

    class Meta:
        ordering = ("id",)

    def get_assessment(self):
        return self.experiment.get_assessment()

    def get_study(self):
        return self.experiment.get_study()

    def clone(self):
        self.id = None
        self.save()
        return self


class ExperimentalDesign(models.Model):
    objects = managers.ExperimentalDesignManager()

    experiment = models.ForeignKey(
        Experiment, on_delete=models.CASCADE, related_name="experimentaldesigns"
    )

    test_system_concentration = models.CharField(
        verbose_name="Test system concentration (e.g. cell density)",
        help_text="Indicate the number of cells or cell density in case of cell lines. Concentration of biological test systems is usually expressed as cell density (amount of cells/cm2 or cells/ml seeded) or confluence (%).",
        max_length=255,
    )

    passage_number = models.CharField(
        help_text="Indicate the passage number only in case that the test system is a cell line, report the passage number(s) used.",
        max_length=255,
        blank=True,
    )

    exposure_medium_composition = models.CharField(
        verbose_name="Composition of exposure medium",
        help_text="Indicate what is the composition of the exposure medium where the test system and test material are incubated together to obtain the result. In case serum is present (not recommended) then please indicate the type and %.",
        max_length=255,
        blank=True,
    )

    incubation_conditions = models.CharField(
        help_text="Indicate cell culture incubation conditions (e.g., temperature, relative humidity, CO2 %, etc.)",
        max_length=255,
        blank=True,
    )

    incubation_conditions = models.CharField(
        help_text="Indicate cell culture incubation conditions (e.g., temperature, relative humidity, CO2 %, etc.)",
        max_length=255,
        blank=True,
    )

    exposure_duration = models.CharField(
        help_text="Indicate the time of incubation / exposure of the test system to the test material.",
        max_length=255,
        blank=True,
    )

    administration_frequency = models.CharField(
        verbose_name="Frequency of Administration",
        help_text="Indicate the frequency of test material administration.",
        max_length=255,
        blank=True,
    )

    technical_replicates = models.CharField(
        verbose_name="Number of technical replicates",
        help_text="Indicate the number of replicates included per concentration test item tested.",
        max_length=255,
        blank=True,
    )

    biological_replicates = models.CharField(
        verbose_name="Number of biological replicates",
        help_text="Indicate the number of biologically independent experiments that were performed. Experiments should be separated in space and time to be considered independent.",
        max_length=255,
        blank=True,
    )

    vessel_type = models.CharField(
        help_text="Indicate the vessel type including size and material (e.g. glass test tube, glass bottom 96 well plate, 384 well polystyrene cell culture plate, etc.",
        max_length=255,
        blank=True,
    )

    remarks = models.CharField(
        verbose_name="Remarks on experimental conditions",
        blank=True,
    )

    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    # TEXT_CLEANUP_FIELDS = "name"

    class Meta:
        ordering = ("id",)

    def get_assessment(self):
        return self.experiment.get_assessment()

    def get_study(self):
        return self.experiment.get_study()

    def __str__(self):
        return self.test_system_concentration

    def clone(self):
        self.id = None
        # self.name = clone_name(self, "name")
        self.save()
        return self


# ExperimentalDesign -> DataAnalysis, etc.
#
# :Subvert/ExperimentalDesign{,s}/DataAnalys{is,es}/g


class DataAnalysis(models.Model):
    objects = managers.DataAnalysisManager()

    experiment = models.ForeignKey(
        Experiment, on_delete=models.CASCADE, related_name="dataanalyses"
    )

    validity = models.CharField(
        verbose_name="Validity / acceptance criteria",
        help_text="Select whether criteria were used for the validity of the experiment and acceptance of the result. If so, please specify the criteria used to accept or reject an experiment or result.",
        choices=constants.YesNoRemarks,
        max_length=2,
        blank=True,
    )

    validity_remarks = models.CharField(
        verbose_name="Validity / acceptance criteria remarks",
        max_length=2000,
        blank=True,
    )

    cytotoxicity = models.CharField(
        verbose_name="Cytotoxicity assay",
        help_text="Was the absence of cytotoxicity confirmed? Select the best answer and provide other relevant details in the remarks field. If yes, specify the type of cytotoxicity assay used.",
        choices=constants.YesNoRemarks,
        max_length=2,
        blank=True,
    )

    cytotoxicity_remarks = models.CharField(
        verbose_name="Cytotoxicity assay remarks",
        max_length=2000,
        blank=True,
    )

    interference_tests = models.CharField(
        help_text="Was the absence of interference from test material confirmed? Select yes in case another type of analysis (other than cytotoxicity) was performed that is important for the interpretation of results (e.g. autofluorescence, quenching, etc.). If yes, specify the type of inference test used.",
        choices=constants.YesNoRemarks,
        max_length=2,
        blank=True,
    )

    interference_tests_remarks = models.CharField(
        max_length=2000,
        blank=True,
    )

    detection_range = models.CharField(
        help_text="Did the (object) measurement fall within the detection range for the method used?",
        choices=constants.YesNoRemarks,
        max_length=2,
        blank=True,
    )

    detection_range_remarks = models.CharField(
        max_length=2000,
        blank=True,
    )

    data_calculation = models.CharField(
        verbose_name="Data calculation and statistics",
        help_text="Is it clear how results are calculated from the raw data?<br>Provide in the remarks field:<br><ul><li>Calculations performed</li><li>Statistical methods used</li><li>Where relevant, provide the method used to exclude outliers</li></ul>",
        choices=constants.YesNoRemarks,
        max_length=2,
        blank=True,
    )

    data_calculation_remarks = models.CharField(
        max_length=2000,
        blank=True,
    )

    evaluation = models.CharField(
        verbose_name="Evaluation / data interpretation criteria",
        help_text="Is there criteria available to determine if the test material resulted as active (or not) in the study? If yes, describe the evaluation criteria used in the study to judge if the test material is positive, negative or equivocal. For example:<p>When there is more than 10% binding to the androgen receptor (as expressed in relative light units) for more than two concentrations, the result is ‘positive’.",
        choices=constants.YesNoRemarks,
        max_length=2,
        blank=True,
    )

    evaluation_remarks = models.CharField(
        max_length=2000,
        blank=True,
    )

    general_remarks = models.CharField(
        verbose_name="Remarks on data analysis",
        max_length=32768,
        blank=True,
    )

    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    # TEXT_CLEANUP_FIELDS = "name"

    class Meta:
        ordering = ("id",)

    def get_assessment(self):
        return self.experiment.get_assessment()

    def get_study(self):
        return self.experiment.get_study()

    """
    def __str__(self):
        return self.test_system_concentration
    """

    def clone(self):
        self.id = None
        self.save()
        return self


class MechanisticEndpoint(BaseEndpoint):
    objects = managers.MechanisticEndpointManager()

    TEXT_CLEANUP_FIELDS = (
        "name",
        "poa_process_other",
        "poa_object_details",
        "poa_action_other",
        "details",
        "aop_details",
        "system",
    )
    # CARGO CULT? what is this bit doing...
    TERM_FIELD_MAPPING = {
        "name": "name_term_id",
        "system": "system_term_id",
        "organ": "organ_term_id",
        "effect": "effect_term_id",
        "effect_subtype": "effect_subtype_term_id",
    }

    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE, related_name="endpoints")

    poa_process = models.CharField(
        verbose_name="Process",
        choices=constants.EndpointProcess,
        max_length=4,
        help_text="Process represents the dynamics of the underlying biological system (e.g., receptor binding) (Ives et al, 2017). The Process is also used to annotate Key events in the Adverse Outcome Pathway Wiki (https://aopwiki.org/) as described in Ives et al, 2017, doi:10.1089/aivt.2017.0017).<p>Select the process that best describes the mechanistic information observed or select ‘other’ to specify the Process and provide a term. Please consult the Ontology Lookup Service (OLS) which is available at https://www.ebi.ac.uk/ols/index to choose a Process term. If possible please select as Process one term belonging to the following ontology Gene Ontology (GO).<p>For most terms there will be several options. It is therefore important to also copy the preferred ontology identifier into the remarks field.<p>Cytotoxicity data should only be reported as a process (e.g. cell death) when it is the scope of the study to determine cytotoxicity. In cases where cytotoxicity is measured for supporting information e.g. for dose selection/elimination, it should not be considered as a process. Such data are reported as ‘Other observations’.",
        blank=True,
    )

    poa_process_other = models.CharField(
        max_length=255, help_text="Enter additional details about Process", blank=True
    )

    poa_object = models.CharField(
        verbose_name="Object",
        choices=constants.EndpointObject,
        max_length=4,
        help_text="Object represents the subject of the observed measurement (biological or chemical), for example, a specific biological receptor that is activated or inhibited, a specific molecule that is being formed and detected or a specific protein that is being bound. The Object is also used to annotate Key events in the Adverse Outcome Pathway Wiki (https://aopwiki.org/) as described in Ives et al, 2017, doi:10.1089/aivt.2017.0017).<p>It is optional to record both Process and Object. If both Process and Object are recorded, they have to be concordant with the chosen Action.<p>Please consult the Ontology Lookup Service (OLS) which is available at https://www.ebi.ac.uk/ols/index to choose a Process term. If possible, please select as Object one term belonging to the following ontologies protein Ontology (PR) or Chemical Entities of Biological Interest (ChEBI).<p> Enter the name and identifier of the object:<p>For most terms there will be several options. It is therefore important to also copy the preferred ontology identifier into the remarks field.<p>More than one object can be provided e.g. when changes of more than one biomarker is measured.<p>Examples of objects are:<br><ul><li>CD86 molecule - [PR:000001412]</li><li>cytochrome P450 - [CHEBI:38559]</li><li>interleukin 8 (IL8) - [PR:000001395]</li><li>thyroid peroxidase (TPO) - [PR:000016584]</li><li>UDP-glucuronosyltransferase (UDP GT) - [PR:000024849]</li></ul>",
        blank=True,
    )

    poa_object_details = models.CharField(
        max_length=255, help_text="Enter additional details about Object", blank=True
    )

    poa_action = models.CharField(
        verbose_name="Action",
        choices=constants.EndpointAction,
        max_length=4,
        help_text="Action represents the type of change observed e.g. ‘‘decrease’’ in the case where a receptor is inhibited to indicate a decrease in the signalling by that receptor. Action is also used to annotate Key events in the Adverse Outcome Pathway Wiki (https://aopwiki.org/) as described in Ives et al, 2017, doi:10.1089/aivt.2017.0017). Action is used together with the field Process and/or Object.<p>The Action field is always required to describe the type of change observed and it can form the following syntaxes “Process, Action” e.g. “gene expression, increase” or “Process, Object, Action” e.g. receptor activity, estrogen receptor, increase.<p>Select the Action that best describes the change observed or select ‘other’ to  specify the action and provide a term.",
        blank=True,
    )

    poa_action_other = models.CharField(
        max_length=255, help_text="Enter additional details about Action", blank=True
    )

    details = models.CharField(
        verbose_name="Details on the effect measured",
        help_text="Enter details about the endpoint that is measured in the (research) study.<br>Describe the (biological) change that is measured and what this means for human health, the environment or wildlife.",
        blank=True,
    )

    links_to_aops = models.CharField(
        help_text="Does the effect identification link to an AOP, MIE, KE, or KER? See https://aopwiki.org/.",
        choices=constants.SimpleYesNo,
        max_length=3,
        blank=True,
    )

    aop_details = models.CharField(
        help_text="Provide details of linked AOP content as available (note, more than one AOP link may be provided):<br><ul><li>AOP name and link</li><li>KE name and link</li><li>KER name and link</li><li>AO name and link</li></ul>",
        blank=True,
    )

    name_term = models.ForeignKey(
        Term,
        related_name="mech_endpoint_name_terms",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    # SYSTEM
    system = models.CharField(
        max_length=128,
        blank=True,
        help_text="Select the specific system where the observed effect(s) play a role.",
    )
    system_term = models.ForeignKey(
        Term,
        related_name="mech_endpoint_system_terms",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    organ = models.CharField(
        max_length=128,
        blank=True,
        verbose_name="Organ (and tissue)",
        help_text="Relevant organ or tissue",
    )
    organ_term = models.ForeignKey(
        Term,
        related_name="mech_endpoint_organ_terms",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    effect = models.CharField(
        max_length=128, blank=True, help_text="Effect, using common-vocabulary"
    )
    effect_term = models.ForeignKey(
        Term,
        related_name="mech_endpoint_effect_terms",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    effect_subtype = models.CharField(
        max_length=128, blank=True, help_text="Effect subtype, using common-vocabulary"
    )
    effect_subtype_term = models.ForeignKey(
        Term,
        related_name="mech_endpoint_effect_subtype_terms",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    remarks = models.CharField(
        help_text="Include any remarks as appropriate.",
        blank=True,
    )

    class Meta:
        ordering = ("id",)

    def get_assessment(self):
        return self.experiment.get_assessment()

    def get_study(self):
        return self.experiment.get_study()

    # will get exposed in the _object_edit_row.html template for use by javascript/template
    @classmethod
    def get_custom_context(cls, assessment, form_context):
        return {
            "vocabulary": cls.get_vocabulary_settings(assessment, form_context),
        }

    def clone(self):
        self.id = None
        self.save()
        return self

    @classmethod
    def get_vocabulary_settings(cls, assessment: Assessment, form: ModelForm) -> str:
        try:
            vocab = VocabularyNamespace(assessment.vocabulary) if assessment.vocabulary else None
            return json.dumps(
                {
                    "vocabulary": vocab.value if vocab else None,
                    "vocabulary_display": vocab.display_name if vocab else None,
                    "object": {
                        "system": form["system"].value() or "",
                        "system_term_id": form["system_term"].value(),
                        "name": form["name"].value() or "",
                        "name_term_id": form["name_term"].value(),
                        "organ": form["organ"].value() or "",
                        "organ_term_id": form["organ_term"].value(),
                        "effect": form["effect"].value() or "",
                        "effect_term_id": form["effect_term"].value(),
                        "effect_subtype": form["effect_subtype"].value() or "",
                        "effect_subtype_term_id": form["effect_subtype_term"].value(),
                    },
                }
            )
        except Exception as e:
            print(e)

    def save(self, *args, **kwargs):
        # ensure our controlled vocabulary terms don't have leading/trailing whitespace
        self.system = self.system.strip()
        self.organ = self.organ.strip()
        self.effect = self.effect.strip()
        self.effect_subtype = self.effect_subtype.strip()
        self.name = self.name.strip()
        super().save(*args, **kwargs)


reversion.register(Experiment)
reversion.register(Chemical)
reversion.register(TestSystem)
reversion.register(Method)
reversion.register(TestDesign)
reversion.register(MechControl)
reversion.register(ExperimentalDesign)
reversion.register(DataAnalysis)
reversion.register(MechanisticEndpoint)
