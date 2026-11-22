from textwrap import dedent
from types import SimpleNamespace

import pytest
from django.contrib.contenttypes.models import ContentType
from model_bakery import baker


@pytest.fixture
def quill_html():
    html = dedent(
        """
            <h1>Header One</h1>
            <h2>Header Two</h2>
            <p>Paragraph text, with <strong>bold</strong>, <em>italics</em>, <a href="www.google.com">links</a>, and <strong><em>combinations</em></strong>.
            <ul>
                <li>Unordered List</li>
            </ul>
            <ol>
                <li>Ordered List</li>
            </ol>
            """
    )
    return html.replace("\n", "")


@pytest.fixture
def study_data(materialized_views):
    """Create an assessment with bioassay data and risk of bias scores using model_bakery."""
    assessment = baker.make("assessment.Assessment")
    metric = baker.make("riskofbias.RiskOfBiasMetric", domain__assessment=assessment, responses=1)

    def make_study(citation: str, assessment=assessment):
        return baker.make(
            "study.Study",
            assessment=assessment,
            short_citation=citation,
            bioassay=True,
            published=True,
        )

    def make_score(study, score: int, is_default: bool = True, metric=metric):
        rob = baker.make("riskofbias.RiskOfBias", study=study, final=True, active=True)
        return baker.make(
            "riskofbias.RiskOfBiasScore",
            riskofbias=rob,
            metric=metric,
            score=score,
            is_default=is_default,
        )

    # study with a bioassay hierarchy and an overridden risk of bias score
    study = make_study("Foo et al. 2020")
    experiment = baker.make(
        "animal.Experiment", study=study, name="Exp 1", chemical="Chem A", type="Ch"
    )
    species = baker.make("assessment.Species", name="Test Rat")
    strain = baker.make("assessment.Strain", species=species, name="Test SD")
    dosing_regime = baker.make(
        "animal.DosingRegime",
        dosed_animals=None,
        route_of_exposure="OR",
        duration_exposure_text="2 years",
    )
    animal_group = baker.make(
        "animal.AnimalGroup",
        experiment=experiment,
        name="Group 1",
        sex="M",
        generation="",
        species=species,
        strain=strain,
        dosing_regime=dosing_regime,
    )
    dose_units = baker.make("assessment.DoseUnits", name="test mg/kg")
    for group_id, dose in enumerate([0, 10]):
        baker.make(
            "animal.DoseGroup",
            dose_regime=dosing_regime,
            dose_units=dose_units,
            dose_group_id=group_id,
            dose=dose,
        )
    endpoint = baker.make(
        "animal.Endpoint",
        animal_group=animal_group,
        name="Endpoint 1",
        system="Liver",
        effect="Weight",
    )
    default_score = make_score(study, 17)
    override_score = make_score(study, 14, is_default=False)
    baker.make(
        "riskofbias.RiskOfBiasScoreOverrideObject",
        score=override_score,
        content_type=ContentType.objects.get_for_model(endpoint),
        object_id=endpoint.id,
    )

    # study with no scores
    none_study = make_study("Baz et al. 2022")

    # separate assessment where every (study, metric) pair has a single score
    unique_assessment = baker.make("assessment.Assessment")
    unique_metric = baker.make(
        "riskofbias.RiskOfBiasMetric", domain__assessment=unique_assessment, responses=1
    )
    unique_study = make_study("Bar et al. 2021", unique_assessment)
    make_score(unique_study, 16, metric=unique_metric)

    materialized_views()
    return SimpleNamespace(
        assessment=assessment,
        metric=metric,
        study=study,
        unique_assessment=unique_assessment,
        unique_metric=unique_metric,
        unique_study=unique_study,
        none_study=none_study,
        default_score=default_score,
        override_score=override_score,
    )
