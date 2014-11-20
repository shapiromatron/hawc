#!/usr/bin/env python
# -*- coding: utf8 -*-

import json
import logging

from django.db import models
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.core.validators import MinValueValidator, MaxValueValidator

import reversion

from assessment.models import BaseEndpoint
from animal.models import DoseUnits
from study.models import Study
from utils.helper import HAWCDjangoJSONEncoder, build_excel_file, build_tsv_file, HAWCdocx


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

    def get_json(self):
        d = {}
        fields = ('age_mean', 'age_sd', 'age_lower', 'age_upper',
                  'fraction_male', 'n', 'starting_n', 'fraction_male_calculated',
                  'age_calculated', 'age_description')
        for field in fields:
            d[field] = getattr(self, field)

        d['sex'] = self.get_sex_display()
        d['age_sd_type'] = self.get_age_sd_type_display()
        d['age_mean_type'] = self.get_age_mean_type_display()
        d['age_lower_type'] = self.get_age_lower_type_display()
        d['age_upper_type'] = self.get_age_upper_type_display()

        d['ethnicity'] = []
        for eth in self.ethnicity.all():
            d['ethnicity'].append(eth.__unicode__())

        return d

    @staticmethod
    def build_export_from_json_header(prefix="-"):
        # used for full-export/import functionalities
        return (prefix+'sex',
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
                prefix+'n')

    @staticmethod
    def build_flat_from_json_dict(dic):
        # used for full-export/import functionalities
        return (dic['sex'],
                '|'.join([unicode(v) for v in dic['ethnicity']]),
                dic['fraction_male'],
                dic['fraction_male_calculated'],
                dic['age_mean'],
                dic['age_mean_type'],
                dic['age_calculated'],
                dic['age_description'],
                dic['age_sd'],
                dic['age_sd_type'],
                dic['age_lower'],
                dic['age_lower_type'],
                dic['age_upper'],
                dic['age_upper_type'],
                dic['n'])

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

    def get_json(self, json_encode=False):
        d = {}
        fields = ('pk', 'description')
        for field in fields:
            d[field] = getattr(self, field)
        if json_encode:
            return json.dumps(d, cls=HAWCDjangoJSONEncoder)
        else:
            return d


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

    def get_json(self, get_parent=True, json_encode=True):
        d = {}
        fields = ('pk', 'name', 'region', 'state')
        for field in fields:
            d[field] = getattr(self, field)

        d['demographics'] = super(StudyPopulation, self).get_json()
        d['design'] = self.get_design_display()
        d['country'] = self.get_country_display()
        d['url'] = self.get_absolute_url()

        d['inclusion_criteria'] = []
        for crit in self.inclusion_criteria.all():
            d['inclusion_criteria'].append(crit.__unicode__())

        d['exclusion_criteria'] = []
        for crit in self.exclusion_criteria.all():
            d['exclusion_criteria'].append(crit.__unicode__())

        d['confounding_criteria'] = []
        for crit in self.confounding_criteria.all():
            d['confounding_criteria'].append(crit.__unicode__())

        if get_parent:
            d['study'] = self.study.get_json(json_encode=False)

        if json_encode:
            return json.dumps(d, cls=HAWCDjangoJSONEncoder)
        else:
            return d

    @staticmethod
    def build_export_from_json_header():
        # used for full-export/import functionalities
        return ('sp-pk',
                'sp-url',
                'sp-name',
                'sp-design',
                'sp-country',
                'sp-region',
                'sp-state',
                'sp-inclusion_criteria',
                'sp-exclusion_criteria',
                'sp-confounding_criteria')  + \
                Demographics.build_export_from_json_header(prefix='sp-')

    @staticmethod
    def build_flat_from_json_dict(dic):
        # used for full-export/import functionalities
        return (dic['pk'],
                dic['url'],
                dic['name'],
                dic['design'],
                dic['country'],
                dic['region'],
                dic['state'],
                '|'.join([unicode(v) for v in dic['inclusion_criteria']]),
                '|'.join([unicode(v) for v in dic['exclusion_criteria']]),
                '|'.join([unicode(v) for v in dic['confounding_criteria']])) + \
                Demographics.build_flat_from_json_dict(dic['demographics'])

    def save(self, *args, **kwargs):
        super(StudyPopulation, self).save(*args, **kwargs)
        endpoint_pks = list(AssessedOutcome.objects
                            .filter(exposure__study_population=self.pk)
                            .values_list('pk', flat=True))
        logging.debug("Resetting cache for assessed outcomes from study population change")
        AssessedOutcome.d_response_delete_cache(endpoint_pks)


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

    def get_json(self, json_encode=False):
        d = {}
        fields = ('pk', 'inhalation', 'dermal', 'oral', 'in_utero', 'iv',
                  'unknown_route', 'exposure_form_definition', 'metric',
                  'metric_description', 'analytical_method',
                  'control_description', 'exposure_description')
        for field in fields:
            d[field] = getattr(self, field)
        d['dose_units'] = self.metric_units.__unicode__()
        d['url'] = self.get_absolute_url()
        if json_encode:
            return json.dumps(d, cls=HAWCDjangoJSONEncoder)
        else:
            return d

    def save(self, *args, **kwargs):
        super(Exposure, self).save(*args, **kwargs)
        endpoint_pks = list(AssessedOutcome.objects
                            .filter(exposure=self.pk)
                            .values_list('pk', flat=True))
        logging.debug("Resetting cache for assessed outcomes from exposure change")
        AssessedOutcome.d_response_delete_cache(endpoint_pks)

    @staticmethod
    def build_export_from_json_header():
        # used for full-export/import functionalities
        return ('exposure-pk',
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
                'exposure-exposure_description')

    @staticmethod
    def build_flat_from_json_dict(dic):
        # used for full-export/import functionalities
        return (dic['pk'],
                dic['url'],
                dic['inhalation'],
                dic['dermal'],
                dic['oral'],
                dic['in_utero'],
                dic['iv'],
                dic['unknown_route'],
                dic['exposure_form_definition'],
                dic['metric'],
                dic['dose_units'],
                dic['metric_description'],
                dic['analytical_method'],
                dic['control_description'],
                dic['exposure_description'])


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
        (2, "supportive"),
        (1, "inconclusive"),
        (0, "not-supportive"))

    DOSE_RESPONSE_CHOICES = (
        (0, "not-applicable"),
        (1, "monotonic"),
        (2, "non-monotonic"),
        (3, "no trend"))

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

    @staticmethod
    def get_cache_names(pks):
        return ['endpoint-json-{pk}'.format(pk=pk) for pk in pks]

    @classmethod
    def d_response_delete_cache(cls, endpoint_pks):
        super(AssessedOutcome, cls).d_response_delete_cache(endpoint_pks)

    def get_absolute_url(self):
        return reverse('epi:assessedoutcome_detail', kwargs={'pk': self.pk})

    def get_json(self, json_encode=True):
        # this is the main "object" for epidemiology; therefore we cache this
        # json representation because it's expensive to create
        cache_name = AssessedOutcome.get_cache_names([self.pk])[0]
        d = cache.get(cache_name)
        if d is None:

            d = {}

            d['endpoint_type'] = 'epi'
            d['study'] = self.exposure.study_population.study.get_json(json_encode=False)
            d['study_population'] = self.exposure.study_population.get_json(json_encode=False)
            d['exposure'] = self.exposure.get_json(json_encode=False)

            fields = ('pk', 'name', 'data_location', 'population_description',
                      'diagnostic_description', 'outcome_n', 'summary',
                      'prevalence_incidence', 'dose_response_details',
                      'statistical_power_details', 'statistical_metric_description')
            for field in fields:
                d[field] = getattr(self, field)

            d['url'] = self.get_absolute_url()
            d['diagnostic'] = self.get_diagnostic_display()
            d['dose_response'] = self.get_dose_response_display()
            d['statistical_power'] = self.get_statistical_power_display()
            d['main_finding_support'] = self.get_main_finding_support_display()

            d['statistical_metric'] = self.statistical_metric.metric
            d['statistical_metric_abbreviation'] = self.statistical_metric.abbreviation
            d['plot_as_log'] = self.statistical_metric.isLog

            d['adjustment_factors'] = []
            for af in self.adjustment_factors.all():
                d['adjustment_factors'].append(af.get_json(json_encode=False))

            d['adjustment_factors_considered'] = []
            for cc in self.confounders_considered.all():
                d['adjustment_factors_considered'].append(cc.get_json(json_encode=False))

            d['aog'] = []
            for aog in self.groups.all():
                d['aog'].append(aog.get_json(main_finding=self.main_finding,
                                             json_encode=False))

            d['tags'] = []
            for tag in self.effects.all():
                d['tags'].append(tag.get_json(json_encode=False))

            logging.info('setting cache: {cache_name}'.format(cache_name=cache_name))
            cache.set(cache_name, d)

        if json_encode:
            return json.dumps(d, cls=HAWCDjangoJSONEncoder)
        else:
            return d

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
        AssessedOutcome.d_response_delete_cache([self.pk])

    def flat_file_row(self):
        d = self.get_json(json_encode=False)
        rows=[]
        for i in xrange(0, len(d['aog'])):
            row = [d['study']['short_citation'],
                   d['study']['study_url'],
                   d['study']['pk'],
                   d['study']['published'],
                   d['study_population']['name'],
                   d['study_population']['pk'],
                   d['study_population']['design'],
                   d['study_population']['url'],
                   d['exposure']['exposure_form_definition'],
                   d['exposure']['metric'],
                   d['exposure']['url'],
                   d['exposure']['dose_units'],
                   d['name'],
                   d['population_description'],
                   d['pk'],
                   d['diagnostic'],
                   d['statistical_metric'],
                   d['statistical_metric_description'],
                   d['summary'],
                   d['dose_response'],
                   d['statistical_power'],
                   d['main_finding_support'],
                   d['aog'][i]['exposure_group']['description'],
                   d['aog'][i]['exposure_group']['comparative_name'],
                   d['aog'][i]['exposure_group']['exposure_group_id'],
                   d['aog'][i]['exposure_group']['exposure_numeric'],
                   d['aog'][i]['pk'], # repeat for data-pivot key
                   d['aog'][i]['pk'],
                   d['aog'][i]['n'],
                   d['aog'][i]['estimate'],
                   d['aog'][i]['lower_ci'],
                   d['aog'][i]['upper_ci'],
                   d['aog'][i]['ci_units'],
                   d['aog'][i]['se'],
                   d['aog'][i]['p_value_text'],
                   d['aog'][i]['p_value'],
                   d['aog'][i]['main_finding']]
            rows.append(row)

        return rows

    @classmethod
    def flat_file_header(cls):
        return ['Study',
                'Study URL',
                'Study Primary Key',
                'Study Published?',
                'Study Population Name',
                'Study Population Key',
                'Design',
                'Study Population URL',
                'Exposure',
                'Exposure Metric',
                'Exposure URL',
                'Dose Units',
                'Assessed Outcome Name',
                'Assessed Outcome Population Description',
                'Assessed Outcome Key',
                'Diagnostic',
                'Statistical Metric',
                'Statistical Metric Description',
                'Outcome Summary',
                'Dose Response',
                'Statistical Power',
                'Support Main Finding',
                'Exposure Group Name',
                'Exposure Group Comparative Description Name',
                'Exposure Group Order',
                'Exposure Group Numeric',
                'Row Key',
                'Assessed Outcome Group Primary Key',
                'N',
                'Estimate',
                'Lower CI',
                'Upper CI',
                'CI units',
                'SE',
                'Statistical Significance',
                'Statistical Significance (numeric)',
                'Main Finding']

    @classmethod
    def get_tsv_file(cls, queryset):
        """
        Construct a tab-delimited version of the selected queryset of endpoints.
        """
        headers = AssessedOutcome.flat_file_header()
        return build_tsv_file(headers, queryset)

    @classmethod
    def get_excel_file(cls, queryset):
        """
        Construct an Excel workbook of the selected queryset of endpoints.
        """
        sheet_name = 'epi'
        headers = AssessedOutcome.flat_file_header()
        data_rows_func = AssessedOutcome.build_excel_rows
        return build_excel_file(sheet_name, headers, queryset, data_rows_func)

    @staticmethod
    def build_excel_rows(ws, queryset, *args, **kwargs):
        """
        Custom method used to build individual excel rows in Excel worksheet
        """
        # write data
        def try_float(str):
            # attempt to coerce as float, else return string
            try:
                return float(str)
            except:
                return str

        row = 0
        for ao in queryset:
            aogs = ao.flat_file_row()
            for aog in aogs:
                row+=1
                for j, val in enumerate(aog):
                    ws.write(row, j, try_float(val))

    @staticmethod
    def epidemiology_word_report(assessment, queryset):
        """
        Prepare an epidemiology Word report, where each row is a separate study
        population and multiple effects are shown for each.
        """

        def build_title(docx, assessment):
            docx.add_heading("Epidemiological evidence for: {0}".format(assessment) , 1)
            docx.add_paragraph(
                "This section contains all epidemiological evidence currently "
                "available for this assessment. Should addition information be "
                "added, it would be included as well.")
            docx.add_page_break()

        def build_header_row(docx):
            tbl = docx.add_table(rows=1, cols=9)
            header = tbl.rows[0].cells
            header[0].text = r"Reference, study location and period"
            header[1].text = r"Total cases/Total controls"
            header[2].text = r"Control-source"
            header[3].text = r"Exposure assessment"
            header[4].text = r"Organ Site"
            header[5].text = r"Exposure Category"
            header[6].text = r"Exposed Cases"
            header[7].text = r"Relative Risk (95% CI)"
            header[8].text = r"Covariants"
            return tbl

        def build_aog_group_rows(aogs):
            txt_names = u""
            txt_cases = u""
            txt_rrs = u""
            for aog in aogs:
                txt_names += u"{0}\n".format(aog['exposure_group']['description'])
                txt_cases += u"{0}\n".format(aog['exposure_group']['demographics']['n'] or u"")
                if aog['lower_ci'] and aog['upper_ci']:
                    txt_rrs += u'{0} ({1}-{2})\n'.format(aog['estimate'],
                                                         aog['lower_ci'],
                                                         aog['upper_ci'])
                else:
                    txt_rrs += u'{0}\n'.format(aog['estimate'])
            return (txt_names, txt_cases, txt_rrs)

        def build_detail_row(tbl, ao):
            d = ao.get_json(json_encode=False)
            row = tbl.add_row()
            row.cells[0].text = d['study']['short_citation']
            row.cells[1].text = unicode(d['study_population']['demographics']['n'])
            row.cells[2].text = 'e'
            row.cells[3].text = 'a'
            row.cells[4].text = 'b'
            group_rows = build_aog_group_rows(d['aog'])
            row.cells[5].text = group_rows[0]
            row.cells[6].text = group_rows[1]
            row.cells[7].text = group_rows[2]
            row.cells[8].text =  ', '.join([itm['description'] for itm in d['adjustment_factors']])

        docx_wrapper = HAWCdocx()
        docx = docx_wrapper.doc
        build_title(docx, assessment)
        tbl = build_header_row(docx)
        for ao in queryset[:3]:  # AJS to change - start with subset
            build_detail_row(tbl, ao)
        return docx_wrapper

    @staticmethod
    def epidemiology_excel_export(queryset):
        # full export of epidemiology dataset, designed for import/export of
        # data using a flat-xls file.
        sheet_name = 'epi'
        headers = AssessedOutcome.epidemiology_excel_export_header(queryset)
        data_rows_func = AssessedOutcome.build_export_rows
        return build_excel_file(sheet_name, headers, queryset, data_rows_func)

    @staticmethod
    def epidemiology_excel_export_header(queryset):
        # build export header column names for full export
        lst = []
        lst.extend(Study.build_export_from_json_header())
        lst.extend(StudyPopulation.build_export_from_json_header())
        lst.extend(Exposure.build_export_from_json_header())
        lst.extend(AssessedOutcome.build_export_from_json_header())
        lst.extend(AssessedOutcomeGroup.build_export_from_json_header())
        return lst

    @staticmethod
    def build_export_rows(ws, queryset, *args, **kwargs):

        # build export data rows for full-export
        def try_float(val):
            if type(val) is bool:
                return val
            try:
                return float(val)
            except:
                return val

        i = 0
        for ao in queryset:
            d = ao.get_json(json_encode=False)
            fields = []
            fields.extend(Study.build_flat_from_json_dict(d['study']))
            fields.extend(StudyPopulation.build_flat_from_json_dict(d['study_population']))
            fields.extend(Exposure.build_flat_from_json_dict(d['exposure']))
            fields.extend(AssessedOutcome.build_flat_from_json_dict(d))
            # build a row for each aog
            for aog in d['aog']:
                i+=1
                new_fields = list(fields)  # clone
                new_fields.extend(AssessedOutcomeGroup.build_flat_from_json_dict(aog))
                for j, val in enumerate(new_fields):
                    ws.write(i, j, try_float(val))

    @staticmethod
    def build_export_from_json_header():
        # used for full-export/import functionalities
        return ('assessed_outcome-pk',
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
                'assessed_outcome-statistical_metric_description')

    @staticmethod
    def build_flat_from_json_dict(dic):
        # used for full-export/import functionalities
        return (dic['pk'],
                dic['url'],
                dic['name'],
                dic['data_location'],
                dic['population_description'],
                '|'.join([unicode(v['name']) for v in dic['tags']]),
                dic['diagnostic'],
                dic['diagnostic_description'],
                dic['outcome_n'],
                dic['summary'],
                dic['prevalence_incidence'],
                '|'.join([unicode(v['description']) for v in dic['adjustment_factors']]),
                '|'.join([unicode(v['description']) for v in dic['adjustment_factors_considered']]),
                dic['main_finding_support'],
                dic['dose_response'],
                dic['dose_response_details'],
                dic['statistical_power'],
                dic['statistical_power_details'],
                dic['statistical_metric'],
                dic['statistical_metric_description'])

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
        max_length=40,
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

    def get_json(self, json_encode=True):
        d = {}
        fields = ('pk', 'description', 'exposure_numeric',
                  'comparative_name', 'exposure_group_id', 'exposure_n')
        for field in fields:
            d[field] = getattr(self, field)

        d['demographics'] = super(ExposureGroup, self).get_json()

        if json_encode:
            return json.dumps(d, cls=HAWCDjangoJSONEncoder)
        else:
            return d

    @staticmethod
    def build_export_from_json_header():
        # used for full-export/import functionalities
        return ('exposure_group-pk',
                'exposure_group-description',
                'exposure_group-exposure_numeric',
                'exposure_group-comparative_name',
                'exposure_group-exposure_group_id',
                'exposure_group-exposure_n')  + \
                Demographics.build_export_from_json_header(prefix='exposure-group-')

    @staticmethod
    def build_flat_from_json_dict(dic):
        # used for full-export/import functionalities
        return (dic['pk'],
                dic['description'],
                dic['exposure_numeric'],
                dic['comparative_name'],
                dic['exposure_group_id'],
                dic['exposure_n']) + \
                Demographics.build_flat_from_json_dict(dic['demographics'])

    def save(self, *args, **kwargs):
        super(ExposureGroup, self).save(*args, **kwargs)
        endpoint_pks = list(AssessedOutcome.objects
                                .filter(exposure=self.exposure)
                                .values_list('pk', flat=True))
        logging.debug("Resetting cache for assessed outcome from exposure-group change")
        AssessedOutcome.d_response_delete_cache(endpoint_pks)


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

    def get_json(self, main_finding, json_encode=True):
        d = {}
        fields = ('pk', 'n', 'estimate', 'se', 'lower_ci', 'upper_ci',
                  'ci_units', 'p_value', 'p_value_text')
        for field in fields:
            d[field] = getattr(self, field)
        d['exposure_group'] = self.exposure_group.get_json(json_encode=False)
        d['main_finding'] = self.exposure_group==main_finding

        if json_encode:
            return json.dumps(d, cls=HAWCDjangoJSONEncoder)
        else:
            return d

    def get_assessment(self):
        return self.assessed_outcome.get_assessment()

    def save(self, *args, **kwargs):
        super(AssessedOutcomeGroup, self).save(*args, **kwargs)
        logging.debug("Resetting cache for assessed outcome from assessed outcome-group change")
        AssessedOutcome.d_response_delete_cache([self.assessed_outcome.pk])

    @staticmethod
    def build_export_from_json_header():
        # used for full-export/import functionalities
        return ('assessed_outcome_group-pk',
                'assessed_outcome_group-n',
                'assessed_outcome_group-estimate',
                'assessed_outcome_group-se',
                'assessed_outcome_group-lower_ci',
                'assessed_outcome_group-upper_ci',
                'assessed_outcome_group-ci_units',
                'assessed_outcome_group-main_finding', # AssessedOutcome.main_finding
                'assessed_outcome_group-p_value_text') + \
                ExposureGroup.build_export_from_json_header()

    @staticmethod
    def build_flat_from_json_dict(dic):
        # used for full-export/import functionalities
        return (dic['pk'],
                dic['n'],
                dic['estimate'],
                dic['se'],
                dic['lower_ci'],
                dic['upper_ci'],
                dic['ci_units'],
                dic['main_finding'],  # AssessedOutcome.main_finding
                dic['p_value_text'])  + \
                ExposureGroup.build_flat_from_json_dict(dic['exposure_group'])


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

    def get_json(self, json_encode=True, get_parent=True):
        d = {}
        fields = ('pk', 'name', 'lit_search_notes',
                  'lit_search_start_date', 'lit_search_end_date',
                  'total_references', 'total_studies_identified', 'notes')
        for field in fields:
            d[field] = getattr(self, field)

        d['url'] = self.get_absolute_url()
        d['protocol_type'] = self.get_protocol_type_display()
        d['lit_search_strategy'] = self.get_lit_search_strategy_display()
        d['inclusion_criteria'] = [unicode(v) for v in self.inclusion_criteria.all()]
        d['exclusion_criteria'] = [unicode(v) for v in self.exclusion_criteria.all()]

        if get_parent:
            d['study'] = self.study.get_json(json_encode=False)

        if json_encode:
            return json.dumps(d, cls=HAWCDjangoJSONEncoder)
        else:
            return d

    @staticmethod
    def build_export_from_json_header():
        # used for full-export/import functionalities
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
    def build_flat_from_json_dict(dic):
        # used for full-export/import functionalities
        return (
            dic['pk'],
            dic['url'],
            dic['name'],
            dic['protocol_type'],
            dic['lit_search_strategy'],
            dic['lit_search_notes'],
            dic['lit_search_start_date'],
            dic['lit_search_end_date'],
            dic['total_references'],
            u'|'.join(dic['inclusion_criteria']),
            u'|'.join(dic['exclusion_criteria']),
            dic['total_studies_identified'],
            dic['notes']
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
    risk_estimate = models.FloatField()
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

    cache_template_object = 'meta-result-{0}'

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
    def get_cache_names(cls, pks):
        return [cls.cache_template_object.format(pk) for pk in pks]

    @classmethod
    def delete_caches(cls, pks):
        names = cls.get_cache_names(pks)
        logging.info("Removing cache: {}".format(', '.join(names)))
        cache.delete_many(names)

    def get_json(self, json_encode=True, get_parent=True):

        cache_name = self.__class__.get_cache_names([self.pk])[0]
        d = cache.get(cache_name)
        if d:
            logging.info('using cache: {}'.format(cache_name))
        else:
            d = {}
            fields = ('pk', 'label', 'health_outcome', 'data_location',
                      'health_outcome_notes', 'exposure_name', 'exposure_details',
                      'number_studies', 'statistical_notes',
                      'n', 'risk_estimate', 'lower_ci', 'upper_ci',
                      'ci_units', 'heterogeneity', 'notes')
            for field in fields:
                d[field] = getattr(self, field)

            d['url'] = self.get_absolute_url()
            d['statistical_metric'] = unicode(self.statistical_metric)
            d['adjustment_factors'] = [unicode(v) for v in self.adjustment_factors.all()]
            d['single_results'] = [v.get_json(json_encode=False) for v in self.single_results.all()]

            if get_parent:
                d['protocol'] = self.protocol.get_json(json_encode=False, get_parent=False)
                d['study'] = self.protocol.study.get_json(json_encode=False)

                #only set if includes parent
                logging.info('setting cache: {}'.format(cache_name))
                cache.set(cache_name, d)

        if json_encode:
            return json.dumps(d, cls=HAWCDjangoJSONEncoder)
        else:
            return d

    @classmethod
    def epidemiology_excel_export(cls, queryset):
        # full export of epidemiology meta-analysis dataset, designed for
        # import/export using a flat-xls file.
        sheet_name = 'epi-meta-analysis'
        headers = cls.epidemiology_excel_export_header()
        data_rows_func = cls.build_export_rows
        return build_excel_file(sheet_name, headers, queryset, data_rows_func)

    @staticmethod
    def epidemiology_excel_export_header():
        # build export header column names for full export
        lst = []
        lst.extend(Study.build_export_from_json_header())
        lst.extend(MetaProtocol.build_export_from_json_header())
        lst.extend(MetaResult.build_export_from_json_header())
        lst.extend(SingleResult.build_export_from_json_header())
        return lst

    def flat_file_row(self):
        d = self.get_json(json_encode=False)
        row = [
            d['study']['short_citation'],
            d['study']['study_url'],
            d['study']['pk'],
            d['study']['published'],

            d['protocol']['pk'],
            d['protocol']['url'],
            d['protocol']['name'],
            d['protocol']['protocol_type'],
            d['protocol']['total_references'],
            d['protocol']['total_studies_identified'],

            d['pk'],  # repeat for data-pivot key
            d['pk'],
            d['url'],
            d['label'],
            d['health_outcome'],
            d['exposure_name'],
            d['number_studies'],
            d['statistical_metric'],
            d['n'],
            d['risk_estimate'],
            d['lower_ci'],
            d['upper_ci'],
            d['ci_units'],
            d['heterogeneity'],
        ]

        return [row]

    @classmethod
    def flat_file_header(cls):
        return [
            'Study',
            'Study URL',
            'Study Primary Key',
            'Study Published?',

            'Protocol Primary Key',
            'Protocol URL',
            'Protocol Name',
            'Protocol Type',
            'Total References',
            'Identified References',

            'Row Key',
            'Result Primary Key',
            'Result URL',
            'Result Label',
            'Health Outcome',
            'Exposure',
            'Result References',
            'Statistical Metric',
            'N',
            'Estimate',
            'Lower CI',
            'Upper CI',
            'CI units',
            'Heterogeneity'
        ]

    @classmethod
    def get_tsv_file(cls, queryset):
        """
        Construct a tab-delimited version of the selected queryset of endpoints.
        """
        headers = cls.flat_file_header()
        return build_tsv_file(headers, queryset)

    @classmethod
    def get_excel_file(cls, queryset):
        """
        Construct an Excel workbook of the selected queryset of endpoints.
        """
        sheet_name = 'epi-meta-analysis'
        headers = cls.flat_file_header()
        data_rows_func = cls.build_excel_rows
        return build_excel_file(sheet_name, headers, queryset, data_rows_func)

    @staticmethod
    def build_excel_rows(ws, queryset, *args, **kwargs):
        """
        Custom method used to build individual excel rows in Excel worksheet
        """
        def try_float(val):
            if type(val) is bool:
                return val
            try:
                return float(val)
            except:
                return val

        for row, mr in enumerate(queryset):
            for col, val in enumerate(mr.flat_file_row()[0]):
                ws.write(row+1, col, try_float(val))

    @staticmethod
    def build_export_rows(ws, queryset, *args, **kwargs):

        # build export data rows for full-export
        def try_float(val):
            if type(val) is bool:
                return val
            try:
                return float(val)
            except:
                return val

        row = 1
        for mr in queryset:
            d = mr.get_json(json_encode=False)
            fields = []
            fields.extend(Study.build_flat_from_json_dict(d['study']))
            fields.extend(MetaProtocol.build_flat_from_json_dict(d['protocol']))
            fields.extend(MetaResult.build_flat_from_json_dict(d))

            if len(d['single_results'])==0:
                # no single results; just print meta-results once
                for j, val in enumerate(fields):
                    ws.write(row, j, try_float(val))
                row += 1
            else:
                # single-results exist; print each meta-result as a new row
                for sr in d['single_results']:
                    new_fields = list(fields)  # clone
                    new_fields.extend(SingleResult.build_flat_from_json_dict(sr))
                    for j, val in enumerate(new_fields):
                        ws.write(row, j, try_float(val))
                    row += 1

    @staticmethod
    def build_export_from_json_header():
        # used for full-export/import functionalities
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
            'meta_result-risk_estimate',
            'meta_result-lower_ci',
            'meta_result-upper_ci',
            'meta_result-ci_units',
            'meta_result-heterogeneity',
            'meta_result-adjustment_factors',
            'meta_result-notes',
        )

    @staticmethod
    def build_flat_from_json_dict(dic):
        # used for full-export/import functionalities
        return (
            dic['pk'],
            dic['url'],
            dic['label'],
            dic['data_location'],
            dic['health_outcome'],
            dic['health_outcome_notes'],
            dic['exposure_name'],
            dic['exposure_details'],
            dic['number_studies'],
            dic['statistical_metric'],
            dic['statistical_notes'],
            dic['n'],
            dic['risk_estimate'],
            dic['lower_ci'],
            dic['upper_ci'],
            dic['ci_units'],
            dic['heterogeneity'],
            u'|'.join( dic['adjustment_factors']),
            dic['notes'],
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
    risk_estimate = models.FloatField(
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

    class Meta:
        ordering = ('-weight', 'exposure_name')

    def __unicode__(self):
        return self.exposure_name

    def save(self, *args, **kwargs):
        super(SingleResult, self).save(*args, **kwargs)
        MetaResult.delete_caches([self.meta_result.pk])

    def get_json(self, json_encode=True):
        d = {}
        fields = ('pk', 'exposure_name', 'weight',
                  'n', 'risk_estimate', 'lower_ci', 'upper_ci',
                  'ci_units', 'notes')
        for field in fields:
            d[field] = getattr(self, field)

        if self.study:
            d['study'] = unicode(self.study)
            d['study_url'] = self.study.get_absolute_url()

        if self.outcome_group:
            # replace results with data from AOG
            # TODO: account for if SE is used
            d['n'] = self.outcome_group.n
            d['risk_estimate'] = self.outcome_group.estimate
            d['lower_ci'] = self.outcome_group.lower_ci
            d['upper_ci'] = self.outcome_group.upper_ci
            # add link to the group
            d['aog_pk'] = self.outcome_group.pk
            d['ao_name'] = unicode(self.outcome_group.assessed_outcome)
            d['ao_url'] = self.outcome_group.assessed_outcome.get_absolute_url()

        if json_encode:
            return json.dumps(d, cls=HAWCDjangoJSONEncoder)
        else:
            return d

    @staticmethod
    def build_export_from_json_header():
        # used for full-export/import functionalities
        return (
            'single_result-pk',
            'single_result-study',
            'single_result-outcome_group',
            'single_result-exposure_name',
            'single_result-weight',
            'single_result-n',
            'single_result-risk_estimate',
            'single_result-lower_ci',
            'single_result-upper_ci',
            'single_result-ci_units',
            'single_result-notes',
        )

    @staticmethod
    def build_flat_from_json_dict(dic):
        # used for full-export/import functionalities
        return (
            dic['pk'],
            dic.get('study', None),
            dic.get('aog_pk', None),
            dic['exposure_name'],
            dic['weight'],
            dic['n'],
            dic['risk_estimate'],
            dic['lower_ci'],
            dic['upper_ci'],
            dic['ci_units'],
            dic['notes'],
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
