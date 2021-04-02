FinalRiskOfBiasScore = (
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
