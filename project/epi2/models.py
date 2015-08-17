#!/usr/bin/env python
# -*- coding: utf8 -*-

import hashlib
import json

from django.db import models
from django.core.urlresolvers import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

import reversion

from assessment.models import BaseEndpoint
from assessment.serializers import AssessmentSerializer
from utils.helper import HAWCDjangoJSONEncoder, SerializerHelper


class Criteria(models.Model):
    assessment = models.ForeignKey(
        'assessment.Assessment')
    description = models.TextField()
    created = models.DateTimeField(
        auto_now_add=True)
    last_updated = models.DateTimeField(
        auto_now=True)

    class Meta:
        ordering = ('description', )
        unique_together = ('assessment', 'description')

    def __unicode__(self):
        return self.description


class AdjustmentFactor(models.Model):
    assessment = models.ForeignKey(
        'assessment.Assessment')
    description = models.TextField()
    created = models.DateTimeField(
        auto_now_add=True)
    last_updated = models.DateTimeField(
        auto_now=True)

    class Meta:
        unique_together = ('assessment', 'description')
        ordering = ('description', )

    def __unicode__(self):
        return self.description


class Ethnicity(models.Model):

    # https://www.fsd1.org/powerschool/Documents/PDFs/Federal_Race_Ethnicity_Guidelines.pdf
    ETHNICITY_CHOICES = (
        ('I', 'American Indian or Alaskan Native'),
        ('A', 'Asian'),
        ('B', 'Black or African American'),
        ('H', 'Hispanic/Latino'),
        ('P', 'Native American of Other Pacific Islander'),
        ('M', 'Two or More Races'),
        ('W', 'White'),
        ('O', 'Other'),
        ('U', 'Unknown/Unspecified'))

    ethnicity = models.CharField(
        max_length=1,
        choices=ETHNICITY_CHOICES)
    created = models.DateTimeField(
        auto_now_add=True)
    last_updated = models.DateTimeField(
        auto_now=True)


class StudyPopulationCriteria(models.Model):
    CRITERIA_TYPE = (
        ("I", "Inclusion"),
        ("E", "Exclusion"),
        ("C", "Confounding")
    )
    criteria = models.ForeignKey('Criteria',
        related_name='spcriteria')
    study_population = models.ForeignKey('StudyPopulation',
        related_name='spcriteria')
    criteria_type = models.CharField(
        max_length=1,
        choices=CRITERIA_TYPE)


class StudyPopulation(models.Model):

    DESIGN_CHOICES = (
        ('CC', 'Case control'),
        ('CR', 'Case report'),
        ('SE', 'Case series'),
        ('CT', 'Controlled trial'),
        ('CS', 'Cross sectional'),
        ('CP', 'Prospective'),
        ('RT', 'Retrospective'),
    )

    # https://www.iso.org/obp/ui/
    COUNTRY_CHOICES = (
        ("AF", u"Afghanistan"),
        ("AX", u"Åland Islands"),
        ("AL", u"Albania"),
        ("DZ", u"Algeria"),
        ("AS", u"American Samoa"),
        ("AD", u"Andorra"),
        ("AO", u"Angola"),
        ("AI", u"Anguilla"),
        ("AQ", u"Antarctica"),
        ("AG", u"Antigua And Barbuda"),
        ("AR", u"Argentina"),
        ("AM", u"Armenia"),
        ("AW", u"Aruba"),
        ("AU", u"Australia"),
        ("AT", u"Austria"),
        ("AZ", u"Azerbaijan"),
        ("BS", u"Bahamas"),
        ("BH", u"Bahrain"),
        ("BD", u"Bangladesh"),
        ("BB", u"Barbados"),
        ("BY", u"Belarus"),
        ("BE", u"Belgium"),
        ("BZ", u"Belize"),
        ("BJ", u"Benin"),
        ("BM", u"Bermuda"),
        ("BT", u"Bhutan"),
        ("BO", u"Bolivia, Plurinational State Of"),
        ("BQ", u"Bonaire, Sint Eustatius And Saba"),
        ("BA", u"Bosnia And Herzegovina"),
        ("BW", u"Botswana"),
        ("BV", u"Bouvet Island"),
        ("BR", u"Brazil"),
        ("IO", u"British Indian Ocean Territory"),
        ("BN", u"Brunei Darussalam"),
        ("BG", u"Bulgaria"),
        ("BF", u"Burkina Faso"),
        ("BI", u"Burundi"),
        ("KH", u"Cambodia"),
        ("CM", u"Cameroon"),
        ("CA", u"Canada"),
        ("CV", u"Cape Verde"),
        ("KY", u"Cayman Islands"),
        ("CF", u"Central African Republic"),
        ("TD", u"Chad"),
        ("CL", u"Chile"),
        ("CN", u"China"),
        ("CX", u"Christmas Island"),
        ("CC", u"Cocos (Keeling) Islands"),
        ("CO", u"Colombia"),
        ("KM", u"Comoros"),
        ("CG", u"Congo"),
        ("CD", u"Congo, The Democratic Republic Of The"),
        ("CK", u"Cook Islands"),
        ("CR", u"Costa Rica"),
        ("CI", u"Côte D'Ivoire"),
        ("HR", u"Croatia"),
        ("CU", u"Cuba"),
        ("CW", u"Curaçao"),
        ("CY", u"Cyprus"),
        ("CZ", u"Czech Republic"),
        ("DK", u"Denmark"),
        ("DJ", u"Djibouti"),
        ("DM", u"Dominica"),
        ("DO", u"Dominican Republic"),
        ("EC", u"Ecuador"),
        ("EG", u"Egypt"),
        ("SV", u"El Salvador"),
        ("GQ", u"Equatorial Guinea"),
        ("ER", u"Eritrea"),
        ("EE", u"Estonia"),
        ("ET", u"Ethiopia"),
        ("FK", u"Falkland Islands (Malvinas)"),
        ("FO", u"Faroe Islands"),
        ("FJ", u"Fiji"),
        ("FI", u"Finland"),
        ("FR", u"France"),
        ("GF", u"French Guiana"),
        ("PF", u"French Polynesia"),
        ("TF", u"French Southern Territories"),
        ("GA", u"Gabon"),
        ("GM", u"Gambia"),
        ("GE", u"Georgia"),
        ("DE", u"Germany"),
        ("GH", u"Ghana"),
        ("GI", u"Gibraltar"),
        ("GR", u"Greece"),
        ("GL", u"Greenland"),
        ("GD", u"Grenada"),
        ("GP", u"Guadeloupe"),
        ("GU", u"Guam"),
        ("GT", u"Guatemala"),
        ("GG", u"Guernsey"),
        ("GN", u"Guinea"),
        ("GW", u"Guinea-Bissau"),
        ("GY", u"Guyana"),
        ("HT", u"Haiti"),
        ("HM", u"Heard Island And Mcdonald Islands"),
        ("VA", u"Holy See (Vatican City State)"),
        ("HN", u"Honduras"),
        ("HK", u"Hong Kong"),
        ("HU", u"Hungary"),
        ("IS", u"Iceland"),
        ("IN", u"India"),
        ("ID", u"Indonesia"),
        ("IR", u"Iran, Islamic Republic Of"),
        ("IQ", u"Iraq"),
        ("IE", u"Ireland"),
        ("IM", u"Isle Of Man"),
        ("IL", u"Israel"),
        ("IT", u"Italy"),
        ("JM", u"Jamaica"),
        ("JP", u"Japan"),
        ("JE", u"Jersey"),
        ("JO", u"Jordan"),
        ("KZ", u"Kazakhstan"),
        ("KE", u"Kenya"),
        ("KI", u"Kiribati"),
        ("KP", u"Korea, Democratic People's Republic Of"),
        ("KR", u"Korea, Republic Of"),
        ("KW", u"Kuwait"),
        ("KG", u"Kyrgyzstan"),
        ("LA", u"Lao People's Democratic Republic"),
        ("LV", u"Latvia"),
        ("LB", u"Lebanon"),
        ("LS", u"Lesotho"),
        ("LR", u"Liberia"),
        ("LY", u"Libya"),
        ("LI", u"Liechtenstein"),
        ("LT", u"Lithuania"),
        ("LU", u"Luxembourg"),
        ("MO", u"Macao"),
        ("MK", u"Macedonia, The Former Yugoslav Republic Of"),
        ("MG", u"Madagascar"),
        ("MW", u"Malawi"),
        ("MY", u"Malaysia"),
        ("MV", u"Maldives"),
        ("ML", u"Mali"),
        ("MT", u"Malta"),
        ("MH", u"Marshall Islands"),
        ("MQ", u"Martinique"),
        ("MR", u"Mauritania"),
        ("MU", u"Mauritius"),
        ("YT", u"Mayotte"),
        ("MX", u"Mexico"),
        ("FM", u"Micronesia, Federated States Of"),
        ("MD", u"Moldova, Republic Of"),
        ("MC", u"Monaco"),
        ("MN", u"Mongolia"),
        ("ME", u"Montenegro"),
        ("MS", u"Montserrat"),
        ("MA", u"Morocco"),
        ("MZ", u"Mozambique"),
        ("MM", u"Myanmar"),
        ("NA", u"Namibia"),
        ("NR", u"Nauru"),
        ("NP", u"Nepal"),
        ("NL", u"Netherlands"),
        ("NC", u"New Caledonia"),
        ("NZ", u"New Zealand"),
        ("NI", u"Nicaragua"),
        ("NE", u"Niger"),
        ("NG", u"Nigeria"),
        ("NU", u"Niue"),
        ("NF", u"Norfolk Island"),
        ("MP", u"Northern Mariana Islands"),
        ("NO", u"Norway"),
        ("OM", u"Oman"),
        ("PK", u"Pakistan"),
        ("PW", u"Palau"),
        ("PS", u"Palestine, State Of"),
        ("PA", u"Panama"),
        ("PG", u"Papua New Guinea"),
        ("PY", u"Paraguay"),
        ("PE", u"Peru"),
        ("PH", u"Philippines"),
        ("PN", u"Pitcairn"),
        ("PL", u"Poland"),
        ("PT", u"Portugal"),
        ("PR", u"Puerto Rico"),
        ("QA", u"Qatar"),
        ("RE", u"Réunion"),
        ("RO", u"Romania"),
        ("RU", u"Russian Federation"),
        ("RW", u"Rwanda"),
        ("BL", u"Saint Barthélemy"),
        ("SH", u"Saint Helena, Ascension And Tristan Da Cunha"),
        ("KN", u"Saint Kitts And Nevis"),
        ("LC", u"Saint Lucia"),
        ("MF", u"Saint Martin (French Part)"),
        ("PM", u"Saint Pierre And Miquelon"),
        ("VC", u"Saint Vincent And The Grenadines"),
        ("WS", u"Samoa"),
        ("SM", u"San Marino"),
        ("ST", u"Sao Tome And Principe"),
        ("SA", u"Saudi Arabia"),
        ("SN", u"Senegal"),
        ("RS", u"Serbia"),
        ("SC", u"Seychelles"),
        ("SL", u"Sierra Leone"),
        ("SG", u"Singapore"),
        ("SX", u"Sint Maarten (Dutch Part)"),
        ("SK", u"Slovakia"),
        ("SI", u"Slovenia"),
        ("SB", u"Solomon Islands"),
        ("SO", u"Somalia"),
        ("ZA", u"South Africa"),
        ("GS", u"South Georgia And The South Sandwich Islands"),
        ("SS", u"South Sudan"),
        ("ES", u"Spain"),
        ("LK", u"Sri Lanka"),
        ("SD", u"Sudan"),
        ("SR", u"Suriname"),
        ("SJ", u"Svalbard And Jan Mayen"),
        ("SZ", u"Swaziland"),
        ("SE", u"Sweden"),
        ("CH", u"Switzerland"),
        ("SY", u"Syrian Arab Republic"),
        ("TW", u"Taiwan, Province Of China"),
        ("TJ", u"Tajikistan"),
        ("TZ", u"Tanzania, United Republic Of"),
        ("TH", u"Thailand"),
        ("TL", u"Timor-Leste"),
        ("TG", u"Togo"),
        ("TK", u"Tokelau"),
        ("TO", u"Tonga"),
        ("TT", u"Trinidad And Tobago"),
        ("TN", u"Tunisia"),
        ("TR", u"Turkey"),
        ("TM", u"Turkmenistan"),
        ("TC", u"Turks And Caicos Islands"),
        ("TV", u"Tuvalu"),
        ("UG", u"Uganda"),
        ("UA", u"Ukraine"),
        ("AE", u"United Arab Emirates"),
        ("GB", u"United Kingdom"),
        ("US", u"United States"),
        ("UM", u"United States Minor Outlying Islands"),
        ("UY", u"Uruguay"),
        ("UZ", u"Uzbekistan"),
        ("VU", u"Vanuatu"),
        ("VE", u"Venezuela, Bolivarian Republic Of"),
        ("VN", u"Viet Nam"),
        ("VG", u"Virgin Islands, British"),
        ("VI", u"Virgin Islands, U.S."),
        ("WF", u"Wallis And Futuna"),
        ("EH", u"Western Sahara"),
        ("YE", u"Yemen"),
        ("ZM", u"Zambia"),
        ("ZW", u"Zimbabwe"))

    study = models.ForeignKey(
        'study.Study',
        related_name="study_populations2")
    name = models.CharField(
        max_length=256)
    design = models.CharField(
        max_length=2,
        choices=DESIGN_CHOICES)
    country = models.CharField(
        max_length=2,
        choices=COUNTRY_CHOICES)
    region = models.CharField(
        max_length=128,
        blank=True)
    state = models.CharField(
        max_length=128,
        blank=True)
    criteria = models.ManyToManyField(
        Criteria,
        through=StudyPopulationCriteria,
        related_name='populations')
    created = models.DateTimeField(
        auto_now_add=True)
    last_updated = models.DateTimeField(
        auto_now=True)

    class Meta:
        ordering = ('name', )

    def get_absolute_url(self):
        return reverse('epi2:sp_detail', kwargs={'pk': self.pk})

    def get_assessment(self):
        return self.study.get_assessment()

    @property
    def inclusion_criteria(self):
        return self.criteria.filter(spcriteria__criteria_type="I")

    @property
    def exclusion_criteria(self):
        return self.criteria.filter(spcriteria__criteria_type="E")

    @property
    def confounding_criteria(self):
        return self.criteria.filter(spcriteria__criteria_type="C")

    def __unicode__(self):
        return self.name


class Outcome(BaseEndpoint):

    DIAGNOSTIC_CHOICES = (
        (0, 'not reported'),
        (1, 'medical professional or test'),
        (2, 'medical records'),
        (3, 'self-reported'))

    study_population = models.ForeignKey(
        StudyPopulation,
        related_name='outcomes')
    data_location = models.CharField(
        max_length=128,
        blank=True,
        help_text="Details on where the data are found in the literature "
                  "(ex: Figure 1, Table 2, etc.)")
    population_description = models.CharField(
        max_length=128,
        help_text='Detailed description of the population being studied for this outcome, '
                  'which may be a subset of the entire study-population. For example, '
                  '"US (national) NHANES 2003-2008, Hispanic children 6-18 years, ♂♀ (n=797)"',
        blank=True)
    diagnostic = models.PositiveSmallIntegerField(
        choices=DIAGNOSTIC_CHOICES)
    diagnostic_description = models.TextField()
    outcome_n = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Outcome N")
    summary = models.TextField(
        blank=True,
        help_text='Summarize main findings of outcome, or describe why no '
                  'details are presented (for example, "no association '
                  '(data not shown)")')
    prevalence_incidence = models.TextField(
        blank=True)

    def get_absolute_url(self):
        return reverse('epi2:outcome_detail', kwargs={'pk': self.pk})


class GroupCollection(models.Model):
    """
    A collection of comparable groups of individuals.
    """
    study_population = models.ForeignKey(
        StudyPopulation,
        related_name='group_collections')
    outcomes = models.ManyToManyField(
        Outcome,
        related_name='group_collections',
        blank=True)
    name = models.CharField(
        max_length=256)
    description = models.TextField(
        blank=True)
    created = models.DateTimeField(
        auto_now_add=True)
    last_updated = models.DateTimeField(
        auto_now=True)

    class Meta:
        ordering = ('name', )

    def get_absolute_url(self):
        return reverse('epi2:gc_detail', kwargs={'pk': self.pk})

    def get_assessment(self):
        return self.study_population.get_assessment()

    def __unicode__(self):
        return self.name


class Group(models.Model):
    """
    A collection of individuals.
    """
    SEX_CHOICES = (
        ("U", "Not reported"),
        ("M", "Male"),
        ("F", "Female"),
        ("B", "Male and Female"))

    IS_CONTROL_CHOICES = (
        (True, "Yes"),
        (False, "No"),
        (None, "N/A"),
    )

    collection = models.ForeignKey(
        GroupCollection,
        related_name="groups")
    group_id = models.PositiveSmallIntegerField()
    name = models.CharField(
        max_length=256)
    numeric = models.FloatField(
        verbose_name='Numerical value (sorting)',
        help_text='Numerical value, can be used for sorting',
        blank=True,
        null=True)
    comparative_name = models.CharField(
        max_length=64,
        verbose_name="Comparative Name",
        help_text='Group and value, displayed in plots, for example '
                  '"1.5-2.5(Q2) vs ≤1.5(Q1)", or if only one group is available, '
                  '"4.8±0.2 (mean±SEM)"',
        blank=True)
    sex = models.CharField(
        max_length=1,
        choices=SEX_CHOICES)
    ethnicity = models.ManyToManyField(
        Ethnicity,
        blank=True)
    n = models.PositiveIntegerField(
        blank=True,
        null=True)
    starting_n = models.PositiveIntegerField(
        blank=True,
        null=True)
    fraction_male = models.FloatField(
        blank=True,
        null=True,
        help_text="Expects a value between 0 and 1, inclusive (leave blank if unknown)",
        validators=[MinValueValidator(0), MaxValueValidator(1)])
    fraction_male_calculated = models.BooleanField(
        default=False,
        help_text="Was the fraction-male value calculated/estimated from literature?")
    isControl = models.NullBooleanField(
        default=None,
        choices=IS_CONTROL_CHOICES,
        help_text="Should this group be interpreted as a null/control group")
    created = models.DateTimeField(
        auto_now_add=True)
    last_updated = models.DateTimeField(
        auto_now=True)

    class Meta:
        ordering = ('collection', 'group_id', )


class Exposure2(models.Model):
    group_collection = models.OneToOneField(
        GroupCollection,
        primary_key=True,
        related_name="exposure")
    inhalation = models.BooleanField(
        default=False)
    dermal = models.BooleanField(
        default=False)
    oral = models.BooleanField(
        default=False)
    in_utero = models.BooleanField(
        default=False)
    iv = models.BooleanField(
        default=False,
        verbose_name="Intravenous (IV)")
    unknown_route = models.BooleanField(
        default=False)
    exposure_form_definition = models.TextField(
        help_text='Name of exposure-route')
    metric = models.TextField(
        verbose_name="Measurement Metric")
    metric_units = models.ForeignKey(
        'assessment.DoseUnits')
    metric_description = models.TextField(
        verbose_name="Measurement Description")
    analytical_method = models.TextField(
        help_text="Include details on the lab-techniques for exposure measurement in samples.")
    control_description = models.TextField()
    exposure_description = models.CharField(
        max_length=128,
        blank=True,
        help_text='May be used to describe the exposure distribution, for '
                  'example, "2.05 µg/g creatinine (urine), geometric mean; '
                  '25th percentile = 1.18, 75th percentile = 3.33"')
    created = models.DateTimeField(
        auto_now_add=True)
    last_updated = models.DateTimeField(
        auto_now=True)

    class Meta:
        ordering = ('exposure_form_definition', )


class GroupNumericalDescriptions(models.Model):

    MEAN_TYPE_CHOICES = (
        (0, None),
        (1, "mean"),
        (2, "geometric mean"),
        (3, "median"),
        (3, "other"))

    VARIANCE_TYPE_CHOICES = (
        (0, None),
        (1, "SD"),
        (2, "SEM"),
        (3, "GSD"),
        (4, "other"))

    LOWER_LIMIT_CHOICES = (
        (0, None),
        (1, 'lower limit'),
        (2, '5% CI'),
        (3, 'other'))

    UPPER_LIMIT_CHOICES = (
        (0, None),
        (1, 'upper limit'),
        (2, '95% CI'),
        (3, 'other'))

    group = models.ForeignKey(
        Group,
        related_name="descriptions")
    mean = models.FloatField(
        blank=True,
        null=True,
        verbose_name='Central estimate')
    mean_type = models.PositiveSmallIntegerField(
        choices=MEAN_TYPE_CHOICES,
        verbose_name="Central estimate type",
        default=0)
    is_calculated = models.BooleanField(
        default=False,
        help_text="Was value calculated/estimated from literature?")
    description = models.CharField(
        max_length=128,
        blank=True,
        help_text="Description if numeric ages do not make sense for this "
                  "study-population (ex: longitudinal studies)")
    variance = models.FloatField(
        blank=True,
        null=True)
    variance_type = models.PositiveSmallIntegerField(
        choices=VARIANCE_TYPE_CHOICES,
        default=0)
    lower = models.FloatField(
        blank=True,
        null=True)
    lower_type = models.PositiveSmallIntegerField(
        choices=LOWER_LIMIT_CHOICES,
        default=0)
    upper = models.FloatField(
        blank=True,
        null=True)
    upper_type = models.PositiveSmallIntegerField(
        choices=UPPER_LIMIT_CHOICES,
        default=0)


class StatisticalMetric(models.Model):
    metric = models.CharField(
        max_length=128,
        unique=True)
    abbreviation = models.CharField(
        max_length=32)
    isLog = models.BooleanField(
        default=True,
        verbose_name="Log-results",
        help_text="When  plotting, use a log base 10 scale")
    order = models.PositiveSmallIntegerField(
        help_text="Order as they appear in option-list")

    class Meta:
        ordering = ('order', )


class ResultAdjustmentFactor(models.Model):
    adjustment_factor = models.ForeignKey('AdjustmentFactor')
    result_measurement = models.ForeignKey('ResultMeasurement')
    included_in_final_model = models.BooleanField(default=True)


class ResultMeasurement(models.Model):

    DOSE_RESPONSE_CHOICES = (
        (0, "not-applicable"),
        (1, "monotonic"),
        (2, "non-monotonic"),
        (3, "no trend"),
        (4, "not reported"))

    STATISTICAL_POWER_CHOICES = (
        (0, 'not reported or calculated'),
        (1, 'appears to be adequately powered (sample size met)'),
        (2, 'somewhat underpowered (sample size is 75% to <100% of recommended)'),
        (3, 'underpowered (sample size is 50 to <75% required)'),
        (4, 'severely underpowered (sample size is <50% required)'))

    outcome = models.ForeignKey(
        Outcome,
        related_name="groups")
    dose_response_details = models.TextField(
        blank=True)
    statistical_power = models.PositiveSmallIntegerField(
        help_text="Is the study sufficiently powered?",
        default=0,
        choices=STATISTICAL_POWER_CHOICES)
    statistical_power_details = models.TextField(
        blank=True)
    statistical_metric = models.ForeignKey(
        StatisticalMetric)
    statistical_metric_description = models.TextField(
        blank=True,
        help_text="Add additional text describing the statistical metric used, if needed.")
    adjustment_factors = models.ManyToManyField(
        AdjustmentFactor,
        through=ResultAdjustmentFactor,
        related_name='outcome_measurements',
        blank=True)
    dose_response = models.PositiveSmallIntegerField(
        verbose_name="Dose Response Trend",
        help_text="Was a dose-response trend observed?",
        default=0,
        choices=DOSE_RESPONSE_CHOICES)
    created = models.DateTimeField(
        auto_now_add=True)
    last_updated = models.DateTimeField(
        auto_now=True)


class GroupResult(models.Model):

    P_VALUE_QUALIFIER_CHOICES = (
        ('<', '<'),
        ('=', '='),
        ('-', 'n.s.'))

    MAIN_FINDING_CHOICES = (
        (3, "not-reported"),
        (2, "supportive"),
        (1, "inconclusive"),
        (0, "not-supportive"))

    measurement = models.ForeignKey(
        ResultMeasurement)
    group = models.ForeignKey(
        Group)
    n = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Individuals in group where outcome was measured")
    estimate = models.FloatField(
        blank=True,
        null=True,
        help_text="Central tendency estimate for group")
    se = models.FloatField(
        blank=True,
        null=True,
        verbose_name='Standard Error (SE)',
        help_text="Standard error estimate for group")
    lower_ci = models.FloatField(
        blank=True,
        null=True,
        verbose_name='Lower CI',
        help_text="Numerical value for lower-confidence interval")
    upper_ci = models.FloatField(
        blank=True,
        null=True,
        verbose_name='Upper CI',
        help_text="Numerical value for upper-confidence interval")
    ci_units = models.FloatField(
        blank=True,
        null=True,
        default=0.95,
        verbose_name='Confidence Interval (CI)',
        help_text='A 95% CI is written as 0.95.')
    p_value_qualifier = models.CharField(
        max_length=1,
        choices=P_VALUE_QUALIFIER_CHOICES,
        default="-",
        verbose_name='p-value qualifier')
    p_value = models.FloatField(
        blank=True,
        null=True,
        verbose_name='p-value')
    created = models.DateTimeField(
        auto_now_add=True)
    last_updated = models.DateTimeField(
        auto_now=True)
    is_main_finding = models.BooleanField(
        blank=True,
        verbose_name="Main finding",
        help_text="Is this the main-finding for this outcome?")
    main_finding_support = models.PositiveSmallIntegerField(
        choices=MAIN_FINDING_CHOICES,
        help_text="Are the results supportive of the main-finding?",
        default=1)

    class Meta:
        ordering = ('measurement', 'group__group_id')
