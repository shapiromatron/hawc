from typing import NamedTuple


class SQL(NamedTuple):
    create: str
    drop: str


FinalRiskOfBiasScore = SQL(
    """
    create materialized view if not exists materialized_finalriskofbiasscore as
    select
        ROW_NUMBER() OVER (ORDER BY score_id, ovr.content_type_id, ovr.object_id) as id,
        scr.id as "score_id",
        scr.score as "score_score",
        scr.is_default,
        rob.study_id,
        scr.metric_id,
        scr.riskofbias_id,
        ovr.content_type_id,
        ovr.object_id
    from riskofbias_riskofbiasscore scr
    left join riskofbias_riskofbias rob
    on scr.riskofbias_id = rob.id
    left join riskofbias_riskofbiasscoreoverrideobject ovr
    on scr.id = ovr.score_id
    where rob.final and rob.active;
    create unique index on materialized_finalriskofbiasscore (id);
    create index on materialized_finalriskofbiasscore (score_id);
    create index on materialized_finalriskofbiasscore (study_id);
    """,
    """
    drop materialized view if exists materialized_finalriskofbiasscore;
    """,
)

EndpointSummary = SQL(
    """
    create materialized view materialized_endpointsummary as
    select
        be.id,
        be.id as endpoint_id,
        be.name,
        en.system,
        en.organ,
        en.effect,
        en.effect_subtype,
        en.data_extracted,
        en."NOEL",
        en."LOEL",
        ag.id as animal_group_id,
        ag.lifestage_exposed,
        ag.lifestage_assessed,
        ag.species_id,
        ag.strain_id,
        ag.sex,
        dr.id as dosing_regime_id,
        ex.id as experiment_id,
        ex.chemical,
        ex.cas,
        st.reference_ptr_id as study_id,
        be.assessment_id
    from animal_endpoint en
    left join assessment_baseendpoint be
    on en.baseendpoint_ptr_id = be.id
    left join animal_animalgroup ag
    on en.animal_group_id = ag.id
    left join animal_dosingregime dr
    on ag.dosing_regime_id = dr.id
    left join animal_experiment ex
    on ag.experiment_id = ex.id
    left join study_study st
    on ex.study_id = st.reference_ptr_id;
    create unique index on materialized_endpointsummary (id);
    create index on materialized_endpointsummary (assessment_id);
    """,
    """
    drop materialized view materialized_endpointsummary;
    """,
)
