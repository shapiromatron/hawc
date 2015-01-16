#!/usr/bin/env python
# -*- coding: utf8 -*-

import hashlib
import json
import logging

from django.db import models
from django.core.urlresolvers import reverse
from django.core.validators import MinValueValidator, MaxValueValidator

import reversion

from assessment.models import BaseEndpoint
from assessment.serializers import AssessmentSerializer
from animal.models import DoseUnits
from utils.helper import HAWCDjangoJSONEncoder, SerializerHelper


class StudyCriteria(models.Model):
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

    def __unicode__(self):
        return self.get_ethnicity_display()


class Demographics(models.Model):

    SEX_CHOICES = (
        ("U", "Not reported"),
        ("M", "Male"),
        ("F", "Female"),
        ("B", "Male and Female"))

    MEAN_TYPE_CHOICES = (
        (0, None),
        (1, "mean"),
        (2, "geometric mean"),
        (3, "median"))

    SD_TYPE_CHOICES = (
        (0, None),
        (1, "SD"),
        (2, "SEM"))

    AGE_LOWER_LIMIT_CHOICES = (
        (0, None),
        (1, 'lower limit'))

    AGE_UPPER_LIMIT_CHOICES = (
        (0, None),
        (1, 'upper limit'))

    sex = models.CharField(
        max_length=1,
        choices=SEX_CHOICES)
    ethnicity = models.ManyToManyField(
        Ethnicity,
        blank=True)
    fraction_male = models.FloatField(
        blank=True,
        null=True,
        help_text="Expects a value between 0 and 1, inclusive (leave blank if unknown)",
        validators=[MinValueValidator(0), MaxValueValidator(1)])
    fraction_male_calculated = models.BooleanField(
        default=False,
        help_text="Was the fraction-male value calculated/estimated from literature?")
    age_mean = models.FloatField(
        blank=True,
        null=True,
        verbose_name='Age central estimate')
    age_mean_type = models.PositiveSmallIntegerField(
        choices=MEAN_TYPE_CHOICES,
        verbose_name="Age central estimate type",
        default=0)
    age_calculated = models.BooleanField(
        default=False,
        help_text="Were age values calculated/estimated from literature?")
    age_description = models.CharField(
        max_length=128,
        blank=True,
        help_text="Age description if numeric ages do not make sense for this "
                  "study-population (ex: longitudinal studies)")
    age_sd = models.FloatField(
        blank=True,
        null=True,
        verbose_name='Age variance')
    age_sd_type = models.PositiveSmallIntegerField(
        choices=SD_TYPE_CHOICES,
        verbose_name="Age variance type",
        default=0)
    age_lower = models.FloatField(
        blank=True,
        null=True)
    age_lower_type = models.PositiveSmallIntegerField(
        choices=AGE_LOWER_LIMIT_CHOICES,
        default=0)
    age_upper = models.FloatField(
        blank=True,
        null=True)
    age_upper_type = models.PositiveSmallIntegerField(
        choices=AGE_UPPER_LIMIT_CHOICES,
        default=0)
    n = models.PositiveIntegerField(
        blank=True,
        null=True)
    starting_n = models.PositiveIntegerField(
        blank=True,
        null=True)
    created = models.DateTimeField(
        auto_now_add=True)
    last_updated = models.DateTimeField(
        auto_now=True)

    class Meta:
        abstract = True

    @staticmethod
    def flat_complete_header_row(prefix="-"):
        return (
            prefix+'sex',
            prefix+'ethnicity',
            prefix+'fraction_male',
            prefix+'fraction_male_calculated',
            prefix+'age_mean',
            prefix+'age_mean_type',
            prefix+'age_calculated',
            prefix+'age_description',
            prefix+'age_sd',
            prefix+'age_sd_type',
            prefix+'age_lower',
            prefix+'age_lower_type',
            prefix+'age_upper',
            prefix+'age_upper_type',
            prefix+'n'
        )

    @staticmethod
    def flat_complete_data_row(ser):
        return (
            ser['sex'],
            '|'.join(ser['ethnicity']),
            ser['fraction_male'],
            ser['fraction_male_calculated'],
            ser['age_mean'],
            ser['age_mean_type'],
            ser['age_calculated'],
            ser['age_description'],
            ser['age_sd'],
            ser['age_sd_type'],
            ser['age_lower'],
            ser['age_lower_type'],
            ser['age_upper'],
            ser['age_upper_type'],
            ser['n']
        )

    def get_ethnicity_list(self):
        eths = []
        for eth in self.ethnicity.all():
            eths.append(eth.get_ethnicity_display())
        return ', '.join(eths)


class Factor(models.Model):
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


class StudyPopulation(Demographics):

    EPI_STUDY_DESIGN_CHOICES = (
        ('CC', 'Case-control'),
        ('CS', 'Cross-sectional'),
        ('CP', 'Prospective'),
        ('RT', 'Retrospective'),
        ('CT', 'Controlled trial'),
        ('SE', 'Case-series'),
        ('CR', 'Case-report'))

    # https://www.iso.org/obp/ui/
    EPI_STUDY_COUNTRY_CHOICES = (
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
        related_name="study_populations")
    name = models.CharField(
        max_length=256)
    design = models.CharField(
        max_length=2,
        choices=EPI_STUDY_DESIGN_CHOICES)
    country = models.CharField(
        max_length=2,
        choices=EPI_STUDY_COUNTRY_CHOICES)
    region = models.CharField(
        max_length=128,
        blank=True)
    state = models.CharField(
        max_length=128,
        blank=True)
    inclusion_criteria = models.ManyToManyField(
        StudyCriteria,
        related_name='inclusion_criteria',
        blank=True,
        null=True)
    exclusion_criteria = models.ManyToManyField(
        StudyCriteria,
        related_name='exclusion_criteria',
        blank=True,
        null=True)
    confounding_criteria = models.ManyToManyField(
        StudyCriteria,
        related_name='confounding_criteria',
        blank=True,
        null=True)

    class Meta:
        ordering = ('name', )

    def __unicode__(self):
        return self.name

    def get_location(self):
        loc = ""
        if self.country:
            loc += self.get_country_display()
        if self.state:
            loc += " ({s})".format(s=self.state)
        if self.region:
            loc += " ({r})".format(r=self.region)
        return loc

    def get_absolute_url(self):
        return reverse('epi:sp_detail', kwargs={'pk': self.pk})

    def get_assessment(self):
        return self.study.get_assessment()

    def get_json(self, json_encode=True):
        return SerializerHelper.get_serialized(self, json=json_encode, from_cache=False)

    @staticmethod
    def flat_complete_header_row():
        return (
            'sp-pk',
            'sp-url',
            'sp-name',
            'sp-design',
            'sp-country',
            'sp-region',
            'sp-state',
            'sp-inclusion_criteria',
            'sp-exclusion_criteria',
            'sp-confounding_criteria'
        )  + Demographics.flat_complete_header_row(prefix='sp-')

    @staticmethod
    def flat_complete_data_row(ser):
        return (
            ser['id'],
            ser['url'],
            ser['name'],
            ser['design'],
            ser['country'],
            ser['region'],
            ser['state'],
            '|'.join(ser['inclusion_criteria']),
            '|'.join(ser['exclusion_criteria']),
            '|'.join(ser['confounding_criteria'])
        ) + Demographics.flat_complete_data_row(ser)

    def save(self, *args, **kwargs):
        super(StudyPopulation, self).save(*args, **kwargs)
        endpoint_pks = AssessedOutcome.objects\
            .filter(exposure__study_population=self.id)\
            .values_list('id', flat=True)
        AssessedOutcome.delete_caches(endpoint_pks)


class Exposure(models.Model):
    study_population = models.ForeignKey(
        StudyPopulation,
        related_name="exposures")
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
        DoseUnits)
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

    def __unicode__(self):
        return self.exposure_form_definition

    def get_absolute_url(self):
        return reverse('epi:exposure_detail', kwargs={'pk': self.pk})

    def get_assessment(self):
        return self.study_population.get_assessment()

    def save(self, *args, **kwargs):
        super(Exposure, self).save(*args, **kwargs)
        endpoint_pks = AssessedOutcome.objects\
            .filter(exposure=self.id)\
            .values_list('id', flat=True)
        AssessedOutcome.delete_caches(endpoint_pks)

    @staticmethod
    def flat_complete_header_row():
        return (
            'exposure-pk',
            'exposure-url',
            'exposure-inhalation',
            'exposure-dermal',
            'exposure-oral',
            'exposure-in_utero',
            'exposure-iv',
            'exposure-unknown_route',
            'exposure-exposure_form_definition',
            'exposure-metric',
            'exposure-metric_units',
            'exposure-metric_description',
            'exposure-analytical_method',
            'exposure-control_description',
            'exposure-exposure_description'
        )

    @staticmethod
    def flat_complete_data_row(ser):
        return (
            ser['id'],
            ser['url'],
            ser['inhalation'],
            ser['dermal'],
            ser['oral'],
            ser['in_utero'],
            ser['iv'],
            ser['unknown_route'],
            ser['exposure_form_definition'],
            ser['metric'],
            ser['metric_units']['units'],
            ser['metric_description'],
            ser['analytical_method'],
            ser['control_description'],
            ser['exposure_description']
        )


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

    def __unicode__(self):
        return self.metric


class AssessedOutcome(BaseEndpoint):

    DIAGNOSTIC_CHOICES = (
        (0, 'not reported'),
        (1, 'medical professional or test'),
        (2, 'medical records'),
        (3, 'self-reported'))

    MAIN_FINDING_CHOICES = (
        (3, "not-reported"),
        (2, "supportive"),
        (1, "inconclusive"),
        (0, "not-supportive"))

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

    exposure = models.ForeignKey(
        Exposure,
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
    summary = models.TextField(blank=True,
        help_text='Summarize main findings of outcome, or describe why no '
                  'details are presented (for example, "no association '
                  '(data not shown)")')
    prevalence_incidence = models.TextField(
        blank=True)
    adjustment_factors = models.ManyToManyField(Factor,
        help_text="All factors which were included in final model",
        related_name='adjustments',
        blank=True, null=True)
    confounders_considered = models.ManyToManyField(Factor,
        verbose_name= "Adjustment factors considered",
        help_text="All factors which were examined "
                  "(including those which were included in final model)",
        related_name='confounders',
        blank=True,
        null=True)
    dose_response = models.PositiveSmallIntegerField(
        verbose_name="Dose Response Trend",
        help_text="Was a dose-response trend observed?",
        default=0,
        choices=DOSE_RESPONSE_CHOICES)
    dose_response_details = models.TextField(
        blank=True)
    statistical_power = models.PositiveSmallIntegerField(
        help_text="Is the study sufficiently powered?",
        default=0,
        choices=STATISTICAL_POWER_CHOICES)
    statistical_power_details = models.TextField(
        blank=True)
    main_finding = models.ForeignKey(
        'epi.ExposureGroup',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="Main finding",
        help_text="When a study did not report a statistically significant "
                  "association use the highest exposure group compared with "
                  "the referent group (e.g., fourth quartile vs. first "
                  "quartile). When a study reports a statistically "
                  "significant association use the lowest exposure group "
                  "with a statistically significant association (e.g., "
                  "third quartile vs. first quartile). When associations "
                  "were non-monotonic in nature, select main findings "
                  "on a case-by-case basis.")
    main_finding_support = models.PositiveSmallIntegerField(
        choices=MAIN_FINDING_CHOICES,
        help_text="Are the results supportive of the main-finding?",
        default=1)
    statistical_metric = models.ForeignKey(
        StatisticalMetric)
    statistical_metric_description = models.TextField(
        blank=True,
        help_text="Add additional text describing the statistical metric used, if needed.")

    @classmethod
    def delete_caches(cls, ids):
        SerializerHelper.delete_caches(cls, ids)

    def get_absolute_url(self):
        return reverse('epi:assessedoutcome_detail', kwargs={'pk': self.pk})

    def get_json(self, json_encode=True):
        return SerializerHelper.get_serialized(self, json=json_encode)

    def get_prior_versions_json(self):
        """ Get prior versions of object. """
        versions = reversion.get_for_object(self)
        versions_json = []
        for version in versions:
            fields = version.field_dict
            try:
                fields['statistical_metric'] = unicode(StatisticalMetric.objects.get(pk=fields['statistical_metric']))
            except Exception:
                fields['statistical_metric'] = "-"
        return json.dumps(versions_json, cls=HAWCDjangoJSONEncoder)

    def save(self, *args, **kwargs):
        super(AssessedOutcome, self).save(*args, **kwargs)
        AssessedOutcome.delete_caches([self.pk])

    @staticmethod
    def flat_complete_header_row():
        return (
            'assessed_outcome-pk',
            'assessed_outcome-url',
            'assessed_outcome-name',
            'assessed_outcome-data_location',
            'assessed_outcome-population_description',
            'assessed_outcome-effects',
            'assessed_outcome-diagnostic',
            'assessed_outcome-diagnostic_description',
            'assessed_outcome-outcome_n',
            'assessed_outcome-summary',
            'assessed_outcome-prevalence_incidence',
            'assessed_outcome-adjustment_factors',
            'assessed_outcome-adjustment_factors_considered',
            'assessed_outcome-main_finding_support',
            'assessed_outcome-dose_response',
            'assessed_outcome-dose_response_details',
            'assessed_outcome-statistical_power',
            'assessed_outcome-statistical_power_details',
            'assessed_outcome-statistical_metric',
            'assessed_outcome-statistical_metric_description'
        )

    @staticmethod
    def flat_complete_data_row(ser):
        return (
            ser['id'],
            ser['url'],
            ser['name'],
            ser['data_location'],
            ser['population_description'],
            '|'.join([unicode(d['name']) for d in ser['effects']]),
            ser['diagnostic'],
            ser['diagnostic_description'],
            ser['outcome_n'],
            ser['summary'],
            ser['prevalence_incidence'],
            '|'.join(ser['adjustment_factors']),
            '|'.join(ser['confounders_considered']),
            ser['main_finding_support'],
            ser['dose_response'],
            ser['dose_response_details'],
            ser['statistical_power'],
            ser['statistical_power_details'],
            ser['statistical_metric']['metric'],
            ser['statistical_metric_description']
        )

    @classmethod
    def get_docx_template_context(cls, assessment, queryset):

        def getStatMethods(ao):
            v = {
                "adjustments_list": ao["adjustments_list"],
                "statistical_metric": ao["statistical_metric"]["metric"],
                "statistical_metric_description": ao["statistical_metric_description"],
                "endpoints": []
            }
            k = u"{}|{}|{}".format(v["adjustments_list"], v["statistical_metric"], v["statistical_metric_description"])
            return hashlib.md5(k.encode('UTF-8')).hexdigest(), v

        outcomes = [
            SerializerHelper.get_serialized(obj, json=False)
            for obj in queryset
        ]
        studies = {}

        # flip dictionary nesting
        for thisAO in outcomes:
            thisExp = thisAO["exposure"]
            thisSP = thisAO["exposure"]["study_population"]
            thisStudy = thisAO["exposure"]["study_population"]["study"]

            study = studies.get(thisStudy["id"])
            if study is None:
                study = thisStudy
                study["sps"] = {}
                studies[study["id"]] = study

            sp = study["sps"].get(thisSP["id"])
            if sp is None:
                sp = thisSP
                sp["ethnicities"] = u', '.join(sp["ethnicity"])
                sp["inclusion_list"] = u', '.join(sp["inclusion_criteria"])
                sp["exclusion_list"] = u', '.join(sp["exclusion_criteria"])
                sp["exposures"] = {}
                study["sps"][sp["id"]]  = sp

            exposure = sp["exposures"].get(thisExp["id"])
            if exposure is None:
                exposure = thisExp
                exposure["aos"] = {}
                exposure["statistical_methods"] = {}
                sp["exposures"][exposure["id"]]  = exposure

            ao = exposure["aos"].get(thisAO["id"])
            if ao is None:
                ao = thisAO
                ao["adjustments_list"] = u', '.join(sorted(ao["adjustment_factors"]))
                exposure["aos"][ao["id"]]  = ao

            key, val = getStatMethods(ao)
            stat_methods = exposure['statistical_methods'].get(key)
            if not stat_methods:
                exposure['statistical_methods'][key] = val
                stat_methods = val
            stat_methods["endpoints"].append(ao["name"])

        # convert value dictionaries to lists
        studies = studies.values()
        for study in studies:
            study["sps"] = study["sps"].values()
            for sp in study["sps"]:
                sp["exposures"] = sp["exposures"].values()
                for exp in sp["exposures"]:
                    exp["aos"] = exp["aos"].values()
                    exp["statistical_methods"] = exp["statistical_methods"].values()
                    for obj in exp["statistical_methods"]:
                        obj["endpoints_list"] = ", ".join(obj["endpoints"])

        return {
            "assessment": AssessmentSerializer().to_representation(assessment),
            "studies": studies
        }


class ExposureGroup(Demographics):
    exposure = models.ForeignKey(
        Exposure,
        related_name='groups')
    description = models.CharField(
        max_length=256)
    exposure_numeric = models.FloatField(
        verbose_name='Low exposure value (sorting)',
        help_text='Should be an exposure-value used for sorting',
        blank=True, null=True)
    comparative_name = models.CharField(
        max_length=64,
        verbose_name="Comparative Name",
        help_text='Should include effect-group and comparative group, for example '
                  '"1.5-2.5(Q2) vs ≤1.5(Q1)", or if only one group is available, '
                  '"4.8±0.2 (mean±SEM)"',
        blank=True)
    exposure_group_id = models.PositiveSmallIntegerField()
    exposure_n = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        help_text="Final N used for exposure group")

    class Meta:
        ordering = ('exposure_group_id', )

    def __unicode__(self):
        return self.description

    def get_assessment(self):
        return self.exposure.get_assessment()

    @staticmethod
    def flat_complete_header_row():
        return (
            'exposure_group-pk',
            'exposure_group-description',
            'exposure_group-exposure_numeric',
            'exposure_group-comparative_name',
            'exposure_group-exposure_group_id',
            'exposure_group-exposure_n'
        ) + Demographics.flat_complete_header_row(prefix='exposure-group-')

    @staticmethod
    def flat_complete_data_row(ser):
        return (
            ser['id'],
            ser['description'],
            ser['exposure_numeric'],
            ser['comparative_name'],
            ser['exposure_group_id'],
            ser['exposure_n']
        ) + Demographics.flat_complete_data_row(ser)

    def save(self, *args, **kwargs):
        super(ExposureGroup, self).save(*args, **kwargs)
        endpoint_pks = AssessedOutcome.objects\
            .filter(exposure=self.exposure)\
            .values_list('id', flat=True)
        AssessedOutcome.delete_caches(endpoint_pks)


class AssessedOutcomeGroup(models.Model):

    P_VALUE_QUALIFIER_CHOICES = (
        ('<', '<'),
        ('=', '='),
        ('-', 'n.s.'))

    exposure_group = models.ForeignKey(
        ExposureGroup,
        help_text="Exposure-group related to this assessed outcome group")
    assessed_outcome = models.ForeignKey(
        AssessedOutcome,
        related_name="groups")
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

    class Meta:
        ordering = ('exposure_group__exposure_group_id', )

    def __unicode__(self):
        txt = u"%s: %s" % (self.exposure_group, self.estimate)
        if self.se:
            txt += u" (SE: %s)" % (self.se)
        if self.lower_ci and self.upper_ci:
             txt += u" (%s-%s)" % (self.lower_ci, self.upper_ci)
        return txt

    @property
    def p_value_text(self):
        txt = self.get_p_value_qualifier_display()
        if txt != "n.s.":
            txt += str(self.p_value)
        return txt

    def get_assessment(self):
        return self.assessed_outcome.get_assessment()

    def save(self, *args, **kwargs):
        super(AssessedOutcomeGroup, self).save(*args, **kwargs)
        AssessedOutcome.delete_caches([self.assessed_outcome.id])

    @property
    def isMainFinding(self):
        return self.assessed_outcome.main_finding_id == self.exposure_group_id

    @staticmethod
    def flat_complete_header_row():
        return (
            'assessed_outcome_group-pk',
            'assessed_outcome_group-n',
            'assessed_outcome_group-estimate',
            'assessed_outcome_group-se',
            'assessed_outcome_group-lower_ci',
            'assessed_outcome_group-upper_ci',
            'assessed_outcome_group-ci_units',
            'assessed_outcome_group-main_finding', # AssessedOutcome.main_finding
            'assessed_outcome_group-p_value_text'
        ) + ExposureGroup.flat_complete_header_row()

    @staticmethod
    def flat_complete_data_row(ser):
        return (
            ser['id'],
            ser['n'],
            ser['estimate'],
            ser['se'],
            ser['lower_ci'],
            ser['upper_ci'],
            ser['ci_units'],
            ser['isMainFinding'],
            ser['p_value_text']
        ) + ExposureGroup.flat_complete_data_row(ser['exposure_group'])


class MetaProtocol(models.Model):

    META_PROTOCOL_CHOICES = (
        (0, "Meta-analysis"),
        (1, "Pooled-analysis"))

    META_LIT_SEARCH_CHOICES = (
        (0, "Systematic"),
        (1, "Other"))

    study = models.ForeignKey('study.Study',
         related_name="meta_protocols")
    name = models.CharField(
        verbose_name="Protocol name",
        max_length=128)
    protocol_type = models.PositiveSmallIntegerField(
        choices=META_PROTOCOL_CHOICES,
        default=0)
    lit_search_strategy = models.PositiveSmallIntegerField(
        verbose_name="Literature search strategy",
        choices=META_LIT_SEARCH_CHOICES,
        default=0)
    lit_search_notes = models.TextField(
        verbose_name="Literature search notes",
        blank=True)
    lit_search_start_date = models.DateField(
        verbose_name="Literature search start-date",
        blank=True,
        null=True)
    lit_search_end_date = models.DateField(
        verbose_name="Literature search end-date",
        blank=True,
        null=True)
    total_references = models.PositiveIntegerField(
        verbose_name="Total number of references found",
        help_text="References identified through initial literature-search "
                  "before application of inclusion/exclusion criteria",
        blank=True,
        null=True)
    inclusion_criteria = models.ManyToManyField(
        StudyCriteria,
        related_name='meta_inclusion_criteria',
        blank=True,
        null=True)
    exclusion_criteria = models.ManyToManyField(
        StudyCriteria,
        related_name='meta_exclusion_criteria',
        blank=True,
        null=True)
    total_studies_identified = models.PositiveIntegerField(
        verbose_name="Total number of studies identified",
        help_text="Total references identified for inclusion after application "
                  "of literature review and screening criteria")
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ('name', )

    def __unicode__(self):
        return self.name

    def get_assessment(self):
        return self.study.get_assessment()

    def get_absolute_url(self):
        return reverse('epi:mp_detail', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        super(MetaProtocol, self).save(*args, **kwargs)
        MetaResult.delete_caches(self.results.all().values_list('pk', flat=True))

    def get_json(self, json_encode=True):
        return SerializerHelper.get_serialized(self, json=json_encode, from_cache=False)

    @staticmethod
    def flat_complete_header_row():
        return (
            'meta_protocol-pk',
            'meta_protocol-url',
            'meta_protocol-name',
            'meta_protocol-protocol_type',
            'meta_protocol-lit_search_strategy',
            'meta_protocol-lit_search_notes',
            'meta_protocol-lit_search_start_date',
            'meta_protocol-lit_search_end_date',
            'meta_protocol-total_references',
            'meta_protocol-inclusion_criteria',
            'meta_protocol-exclusion_criteria',
            'meta_protocol-total_studies_identified',
            'meta_protocol-notes',
        )

    @staticmethod
    def flat_complete_data_row(ser):
        return (
            ser['id'],
            ser['url'],
            ser['name'],
            ser['protocol_type'],
            ser['lit_search_strategy'],
            ser['lit_search_notes'],
            ser['lit_search_start_date'],
            ser['lit_search_end_date'],
            ser['total_references'],
            u'|'.join(ser['inclusion_criteria']),
            u'|'.join(ser['exclusion_criteria']),
            ser['total_studies_identified'],
            ser['notes']
        )


class MetaResult(models.Model):
    protocol = models.ForeignKey(
        MetaProtocol,
        related_name="results")
    label = models.CharField(
        max_length=128)
    data_location = models.CharField(
        max_length=128,
        blank=True,
        help_text="Details on where the data are found in the literature "
                  "(ex: Figure 1, Table 2, etc.)")
    health_outcome = models.CharField(
        max_length=128)
    health_outcome_notes = models.TextField(
        blank=True)
    exposure_name = models.CharField(
        max_length=128)
    exposure_details = models.TextField(
        blank=True)
    number_studies = models.PositiveSmallIntegerField()
    statistical_metric = models.ForeignKey(
        StatisticalMetric)
    statistical_notes = models.TextField(
        blank=True)
    n = models.PositiveIntegerField(
        help_text="Number of individuals included from all analyses")
    estimate = models.FloatField()
    lower_ci = models.FloatField(
        verbose_name="Lower CI",
        help_text="Numerical value for lower-confidence interval")
    upper_ci = models.FloatField(
        verbose_name="Upper CI",
        help_text="Numerical value for upper-confidence interval")
    ci_units = models.FloatField(
        blank=True,
        null=True,
        default=0.95,
        verbose_name='Confidence Interval (CI)',
        help_text='A 95% CI is written as 0.95.')
    heterogeneity = models.CharField(
        max_length=256,
        blank=True)
    adjustment_factors = models.ManyToManyField(
        Factor,
        help_text="All factors which were included in final model",
        related_name='meta_adjustments',
        blank=True,
        null=True)
    notes = models.TextField(
        blank=True)

    class Meta:
        ordering = ('label', )

    def __unicode__(self):
        return self.label

    def get_assessment(self):
        return self.protocol.get_assessment()

    def get_absolute_url(self):
        return reverse('epi:mr_detail', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        super(MetaResult, self).save(*args, **kwargs)
        MetaResult.delete_caches([self.pk])

    @classmethod
    def delete_caches(cls, pks):
        SerializerHelper.delete_caches(cls, pks)

    def get_json(self, json_encode=True):
        return SerializerHelper.get_serialized(self, json=json_encode)

    @staticmethod
    def flat_complete_header_row():
        return (
            'meta_result-pk',
            'meta_result-url',
            'meta_result-label',
            'meta_result-data_location',
            'meta_result-health_outcome',
            'meta_result-health_outcome_notes',
            'meta_result-exposure_name',
            'meta_result-exposure_details',
            'meta_result-number_studies',
            'meta_result-statistical_metric',
            'meta_result-statistical_notes',
            'meta_result-n',
            'meta_result-estimate',
            'meta_result-lower_ci',
            'meta_result-upper_ci',
            'meta_result-ci_units',
            'meta_result-heterogeneity',
            'meta_result-adjustment_factors',
            'meta_result-notes',
        )

    @staticmethod
    def flat_complete_data_row(ser):
        return (
            ser['id'],
            ser['url'],
            ser['label'],
            ser['data_location'],
            ser['health_outcome'],
            ser['health_outcome_notes'],
            ser['exposure_name'],
            ser['exposure_details'],
            ser['number_studies'],
            ser['statistical_metric']['metric'],
            ser['statistical_notes'],
            ser['n'],
            ser['estimate'],
            ser['lower_ci'],
            ser['upper_ci'],
            ser['ci_units'],
            ser['heterogeneity'],
            u'|'.join(ser['adjustment_factors']),
            ser['notes'],
        )

    @classmethod
    def get_docx_template_context(cls, queryset):
        return {
            "field1": "body and mind",
            "field2": "well respected man",
            "field3": 1234,
            "nested": {"object": {"here": u"you got it!"}},
            "extra": "tests",
            "tables": [
                {
                    "title": "Tom's table",
                    "row1": 'abc',
                    "row2": 'def',
                    "row3": 123,
                    "row4": 6/7.,
                },
                {
                    "title": "Frank's table",
                    "row1": 'abc',
                    "row2": 'def',
                    "row3": 223,
                    "row4": 5/7.,
                },
                {
                    "title": "Gerry's table",
                    "row1": 'cats',
                    "row2": 'dogs',
                    "row3": 123,
                    "row4": 4/7.,
                },
            ]
        }


class SingleResult(models.Model):
    meta_result = models.ForeignKey(
        MetaResult,
        related_name="single_results")
    study = models.ForeignKey(
        'study.Study',
        related_name="single_results",
        blank=True,
        null=True)
    outcome_group = models.ForeignKey(
        AssessedOutcomeGroup,
        related_name="single_results",
        blank=True,
        null=True)
    exposure_name = models.CharField(
        max_length=128,
        help_text='Enter a descriptive-name for the single study result '
                  '(e.g., "Smith et al. 2000, obese-males")')
    weight = models.FloatField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0),MaxValueValidator(1)],
        help_text="For meta-analysis, enter the fraction-weight assigned for "
                  "each result (leave-blank for pooled analyses)")
    n = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Enter the number of observations for this result")
    estimate = models.FloatField(
        blank=True,
        null=True,
        help_text="Enter the numerical risk-estimate presented for this result")
    lower_ci = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Lower CI",
        help_text="Numerical value for lower-confidence interval")
    upper_ci = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Upper CI",
        help_text="Numerical value for upper-confidence interval")
    ci_units = models.FloatField(
        blank=True,
        null=True,
        default=0.95,
        verbose_name='Confidence Interval (CI)',
        help_text='A 95% CI is written as 0.95.')
    notes = models.TextField(
        blank=True)

    def __unicode__(self):
        return self.exposure_name

    def save(self, *args, **kwargs):
        super(SingleResult, self).save(*args, **kwargs)
        MetaResult.delete_caches([self.meta_result.pk])

    @staticmethod
    def flat_complete_header_row():
        return (
            'single_result-pk',
            'single_result-study',
            'single_result-outcome_group',
            'single_result-exposure_name',
            'single_result-weight',
            'single_result-n',
            'single_result-estimate',
            'single_result-lower_ci',
            'single_result-upper_ci',
            'single_result-ci_units',
            'single_result-notes',
        )

    @staticmethod
    def flat_complete_data_row(ser):

        study = None
        try:
            study = ser['study']['id']
        except TypeError:
            pass

        aog = None
        try:
            aog = ser['outcome_group']['id']
        except TypeError:
            pass

        return (
            ser['id'],
            study,
            aog,
            ser['exposure_name'],
            ser['weight'],
            ser['n'],
            ser['estimate'],
            ser['lower_ci'],
            ser['upper_ci'],
            ser['ci_units'],
            ser['notes'],
        )


reversion.register(Ethnicity)
reversion.register(Factor)
reversion.register(StudyPopulation)
reversion.register(StudyCriteria)
reversion.register(Exposure)
reversion.register(AssessedOutcome,
    follow=('groups', 'adjustment_factors', 'confounders_considered', 'baseendpoint_ptr'))
reversion.register(ExposureGroup)
reversion.register(AssessedOutcomeGroup, follow=('assessed_outcome', ))
reversion.register(MetaProtocol,
    follow=('inclusion_criteria', 'exclusion_criteria'))
reversion.register(MetaResult, follow=('adjustment_factors', ))
reversion.register(SingleResult)
