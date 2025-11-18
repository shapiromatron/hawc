# import reversion
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.urls import reverse

# from ..assessment.models import DSSTox
from ..common.helper import SerializerHelper
from ..common.models import NumericTextField, clone_name

from ..epi.models import Country
from ..study.models import Study
from . import constants  # , managers


# aka LongFormName=="Monitoring Extraction-2019"
class Extraction(models.Model):
    # objects = managers.ExtractionManager()

    study = models.ForeignKey(
        Study, on_delete=models.CASCADE, related_name="exposure_monitoring_extractions"
    )

    # SKIP - review_type
    # SKIP - ir_status
    # SKIP - qc_status
    # SKIP - qc_needed
    # SKIP - qc_type
    # SKIP - correct_study_type

    # do we want PECO fields? Are they of use beyond in terms of manual QC triggering? Hard for me to tell from Distiller form...

    # checkboxes in Distiller form suggest ArrayField in HAWC; should we really support multiple entries here or should this be just a simple CharField? (basically asking if we need to support multiple answers here)
    peco_type = ArrayField(
        models.CharField(max_length=2, choices=constants.PecoType),
        help_text="What is the correct PECO?",
        # verbose_name="Correct PECO",
    )

    peco_supplemental_type = ArrayField(
        models.CharField(max_length=2, choices=constants.PecoSupplementalType),
        help_text="Select Type of PECO Supplemental",
    )

    # SKIP - qc_note -- seems to fall into the "we don't want to bring over meta-fields relating to workflow" category

    study_types = ArrayField(
        models.CharField(max_length=3, choices=constants.StudyType),
        help_text="What are the correct study types?",
    )

    consumer_prod_dermal_flux = ArrayField(
        models.CharField(max_length=3, choices=constants.ConsumerProdDermalFlux),
        verbose_name = "Is there data available for consumer products/articles, dermal parameters, or fluxes?",
        help_text="This can include either primary or secondary source information, and is likely information that is considered PECO Supplemental or contextual (i.e., would not be evaluated under any study type) unless it is primary source concentration data or survey data.",
    )

    brief_description = models.TextField(verbose_name="Briefly describe the information present in the paper", blank=True)

    help_requested = models.BooleanField(verbose_name="Have you discussed this evaluation or extraction with a team lead?", default=False)

    help_requested_discussion_notes = models.TextField(verbose_name="Please list team member and brief summary of resolution.", blank=True)

# aka LongFormName=="Chemical: Inventory Monitoring Subform_2019"
class Chemical(models.Model):
    # objects = managers.ChemicalManager()

    extraction = models.ForeignKey(Extraction, on_delete=models.CASCADE, related_name="chemicals")

    inventory_item_type = models.CharField(
        max_length=3, choices=constants.ChemicalInventoryItemType
    )

    name = models.CharField(
        max_length=256,
        verbose_name="Reported chemical name",
    )

    abbreviation = models.CharField(
        max_length=32,
        verbose_name="Reported chemical abbreviation",
    )

    tsca_chemical_substance = models.CharField(
        max_length=5,
        choices=constants.TSCAChemicalSubstance,
    )

    chemical_form = models.CharField(
        verbose_name = "Form of reported chemical",
        max_length=3,
        choices=constants.ChemicalForm,
    )

    extraction_target = models.CharField(
        verbose_name = "Targeted Metabolite/Degradant to Extract",
        max_length=7,
        choices=constants.TargetedMetaboliteOrDegradant,
    )

# aka LongFormName=="Chemical: Inventory Monitoring Subform_2019"
class Location(models.Model):
    # objects = managers.LocationManager()

    extraction = models.ForeignKey(Extraction, on_delete=models.CASCADE, related_name="locations")

    label = models.CharField(
        max_length=64,
        verbose_name="Location Label (KEY)",
    )

    # checkboxes in data dictionary (ManyToManyField) but feels like should actually be a single?
    countries = models.ManyToManyField(
        Country,
        blank=True,
        related_name="expomon_locations",
    )

    city_state_region = models.CharField(
        max_length=128,
        verbose_name="\"City, State\" or Region"
    )

    coords_provided = models.BooleanField(verbose_name="Are geographic coordinates (lat/longs) provided?", default=False)

    geographic_setting = ArrayField(
        models.CharField(max_length=2, choices=constants.GeographicSetting),
    )

    is_data_for_cohort = models.BooleanField(help_text="Is the data for a cohort?", default=False)

    # TODO cohort name. Idea is user starts typing and dropdown autocompletes; so
    # it should save someplace; what's most HAWC-like way to do this?

    comments = models.TextField(verbose_name="Additional notes for location/cohort.", blank=True)



"""
media models/subforms are a work in progress. See email thread between tfeiler and ashapiro, September 9/17 2025.

tfeiler floated idea of inheritance for the 16 media subforms (AmbientAirMedia, SedimentMedia, etc.)

Relevant excerpts:

-----

            TFEILER: "So let’s finally describe the issue – it’s with that sub_type field; typically we define those as int/char fields and then define the choices in constants.py; user sees a dropdown to pick from. But, after searching docs and forums, I cannot find a good way to override the choices for the subclasses – and ambient air / sediment / etc. have different subtypes (upper air/surface air vs. porewater/bedbottomsurface/etc.). Options I can think of / have found:"
             
            TFEILER: "1. Define it on the parent abstract model with choices; make choices enormous, including every media’s subtype. When we eventually define the forms, we restrict the choices to only those appropriate for that media."
            ASHAPIRO: "I actually like this approach in terms of simplicity of maintenance. And then basically there’d be a dropdown list that would say “add ambient air” etc for all the different subfields, and then there’d be a different Django model form for each subfield. It makes the model more complicated, but downstream queries are simpler. Alternatively, you could have a single Django form, and then dynamically on the frontend w/ JS where the form would change what’s visible and disabled based on the sub_type selection in the user, and then you’d duplicate the validation logic in the form clean method.

            TFEILER: "2. Define it on the parent abstract model without choices (e.g. just a varchar). Again, we could rig up an appropriate dropdown when we build the form, but do we lose any automatic Django benefits by not specifying it at all at the model level?"
            ASHAPIRO: "I think this is similar to the JSON field concept w/ a pydantic schema, or perhaps even better, using the User Defined Fields concept that we developed here. That could also work, but I think I’d prefer option #1. You can see how we did it with studies here, https://github.com/shapiromatron/hawc/blob/5ccbe08a8c3be6efec31931b75d0c69d66f3297c/hawc/apps/study/models.py#L119, but instead of allow a user to pick their own form, we could predefine them. https://github.com/shapiromatron/hawc/commit/ab9cdfbf4ab3e65f0dfb4a856e449670617191f1"

            TFEILER: "3. Move it out of the parent abstract model and define on the subclass. We still get some benefit of the inheritance on the shared fields that aren’t subject to this issue, but we are now duplicating at least that field."
            ASHAPIRO: <no reply>

            TFEILER: "4. Abandon this and just do it as 16 separate ones that inherit from models.Model. Definitely works but even more duplicated fields."
            ASHAPIRO: "Yikes, do not recommend."

            ASHAPIRO GENERAL COMMENTS: "The inheritance works ok in djagno – but it makes things confusing downstream.  We use inheritance for the lit.Reference -> study.Study model, and even though it’s technically possible, I don’t think I like the pattern that much.  If I were doing things over, I don’t think I’d use the pattern.
             
            I think a better approach that we did in HERO was to basically have a single model and either 1) lots of optional fields w/ form logic to toggle which to show based on media type, or 2) a JSON field with a pydantic schema that would allow you to select which additional subfields needed to populate the media-specific tables, or 3) adding a new triple data store concept where some fields would be required.   In terms of simplicity, I’d try to do #1 if that’s possible, and then fall back to #2 if it’s not possible.
             
            The reason I like this more than the subtables, is if you want all the exposures, you can do it in a single query, instead of 16 queries and joins across tables."

-----

We then paused this work due to a combination of staff turnover, funding, gov't shutdown delays, etc.

!!!!!!!! When we pick this up, plan is to NOT do inheritance -- make ExpoMonMedia just cover every subform.
Things like sub_type will have a lot of extra choices and we'll just rely on UI/validation to only
show appropriate ones. Similarly, fields that only make sense for ambient air or sediment or whatever will be
shown/hidden/validated/ignored/etc. based on the context, but the single ExpoMonMedia
will hold all those fields. ExpoMonMedia will have a "media_type" field that tells us if it's
ambient air, sediment, etc. Maybe some configured instead of hand-coded behavior. e.g. something like (pseudocode):

LEGAL_MEDIA_TYPES = ["ambient_air", "sediment", "groundwater", "drinkingwater", "etc"]
class ExpoMonMedia(models.Model):
    class Meta:
        abstract = True

    ##### fields that all subtypes use; add to UNIVERSAL_FIELDS
    extraction = models.ForeignKey(Extraction, on_delete=models.CASCADE)# , related_name="media")
    sub_type = models.PositiveSmallIntegerField( default=0, choices=constants.PlaceholderChoices) # choices should probably be combined all subchoices!
    MEDIA_KEY = # generic, replaces separate DUST_KEY, GROUNDWATER_KEY, etc.
    MEDIA_TYPE = # from LEGAL_MEDIA_TYPES
    SAMPLE_METHOD, SAMPLE_DURATION, etc. # I think these appear on all, but doublecheck!
    media_label = models.CharField( max_length=64, verbose_name="Media Label (KEY)",)
    additional_notes = models.TextField(verbose_name="Additional notes", blank=True)

    ##### fields that only some subtypes use; see FIELDS_BY_MEDIA_TYPE
    num_sites # number
    waterbody_name: # str
    particle_size: # number
    num_participants: # number

    ##### CONFIGURATIONS TO HELP US DRIVE THIS FLEXIBILITY
    UNIVERSAL_FIELDS = [ "extraction", "sub_type", "MEDIA_KEY", etc. ]

    # map of media sub_type -> list of non-univeral fields that this subtype uses.
    # So surface water uses universal fields like "key, sample_method, etc." but also "num_sites, wbname, etc."
    FIELDS_BY_MEDIA_TYPE = {
        "personal_inhalation": [ "num_sites", "particle_size", etc. ],
        "surface_water": ["num_sites", "waterbody_name", etc. ]
        "human_biomonitoring": [ "num_participants", etc. ]
    }

    # map of fieldname -> map of media sub_type -> vals
    # maybe could accomplish this purely via naming convention, but explicit wording is more understandable and not a big burden to maintain.
    CHOICE_OVERRIDES = {
        "sub_type": {
            "ambient_air": constants.AMBIENT_AIR_SUBTYPES,
            "sediment": constants.SEDIMENT_SUBTYPES,
        },
        "some_other_dropdown": {
            "ambient_air": constants.SOMEOTHER_CHOICES,
        }
        # etc.
    }

"""



class ExpoMonMedia(models.Model):
    class Meta:
        abstract = True

    extraction = models.ForeignKey(Extraction, on_delete=models.CASCADE)# , related_name="media")
    sub_type = models.PositiveSmallIntegerField( default=0, choices=constants.PlaceholderChoices)
    media_label = models.CharField( max_length=64, verbose_name="Media Label (KEY)",)
    additional_notes = models.TextField(verbose_name="Additional notes", blank=True)


class AmbientAirMedia(ExpoMonMedia):

    particle_size = models.CharField(
        max_length=256,
        help_text="Enter the phase (gas, particulate) if the particle size is not reported.",
    )

class SedimentMedia(ExpoMonMedia):

    water_body_name = models.CharField(
        max_length=256,
        help_text="Examples: \"Lake Erie\" or \"Multiple tributaries of the Mississippi River\""
    )



# reversion.register(Extraction)
