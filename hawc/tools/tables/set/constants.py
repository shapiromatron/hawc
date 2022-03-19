from enum import Enum


class DataSourceChoices(Enum):
    Animal = "ani"
    Study = "study"


class AttributeChoices(Enum):
    FreeHtml = "free_html"
    Rob = "rob"
    StudyShortCitation = "study_short_citation"
    AnimalGroupDescription = "animal_group_description"
    AnimalGroupDoses = "animal_group_doses"
    ExperimentName = "experiment_name"
    AnimalGroupName = "animal_group_name"
    AnimalGroupTreatmentPeriod = "animal_group_treatment_period"
    AnimalGroupRouteOfExposure = "animal_group_route_of_exposure"
    EndpointSystem = "endpoint_system"
    EndpointEffect = "endpoint_effect"
    EndpointName = "endpoint_name"
    ExperimentChemical = "experiment_chemical"


class RowTypeChoices(Enum):
    Study = "study"
    Experiment = "experiment"
    AnimalGroup = "animal_group"
