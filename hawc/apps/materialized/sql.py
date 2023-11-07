from typing import NamedTuple


class SQL(NamedTuple):
    create: str
    drop: str


FinalRiskOfBiasScore = SQL(
    """
    CREATE MATERIALIZED VIEW IF NOT EXISTS materialized_finalriskofbiasscore AS
    SELECT
        ROW_NUMBER() OVER (ORDER BY score_id, ovr.content_type_id, ovr.object_id) as id,
        scr.id as "score_id",
        scr.label as "score_label",
        scr.notes as "score_notes",
        scr.score as "score_score",
        scr.bias_direction,
        scr.is_default,
        rob.study_id,
        scr.metric_id,
        scr.riskofbias_id,
        ovr.content_type_id,
        ovr.object_id
    FROM riskofbias_riskofbiasscore scr
    LEFT join riskofbias_riskofbias rob
    ON scr.riskofbias_id = rob.id
    LEFT JOIN riskofbias_riskofbiasscoreoverrideobject ovr
    ON scr.id = ovr.score_id
    WHERE rob.final AND rob.active
    ORDER BY scr.id, ovr.id;

    CREATE UNIQUE INDEX ON materialized_finalriskofbiasscore (id);
    CREATE INDEX ON materialized_finalriskofbiasscore (score_id);
    CREATE INDEX ON materialized_finalriskofbiasscore (study_id);
    """,
    """
    DROP MATERIALIZED VIEW IF EXISTS materialized_finalriskofbiasscore;
    """,
)
