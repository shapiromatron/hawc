from django.db import migrations


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("riskofbias", "0022_new_rob_scores"),
    ]

    operations = [
        migrations.RunSQL(
            """
            create materialized view materialized_finalriskofbiasscore as
            select
                ROW_NUMBER() OVER (ORDER BY scrs.score_id, scrs.content_type_id, scrs.object_id) as id,
                scrs.*,
                rob.study_id
            from (
                (select
                    scr.id as "score_id",
                    scr.score as "score_score",
                    scr.is_default,
                    scr.metric_id,
                    scr.riskofbias_id,
                    NULL as "content_type_id",
                    NULL as "object_id"
                from riskofbias_riskofbiasscore scr)
                union
                (select
                    scr.id as "score_id",
                    scr.score as "score_score",
                    scr.is_default,
                    scr.metric_id,
                    scr.riskofbias_id,
                    ovr.content_type_id,
                    ovr.object_id
                from riskofbias_riskofbiasscore scr
                inner join riskofbias_riskofbiasscoreoverrideobject ovr
                on scr.id = ovr.score_id)
            ) scrs
            left join riskofbias_riskofbias rob
            on scrs.riskofbias_id = rob.id
            where rob.final and rob.active;
            create unique index on materialized_finalriskofbiasscore (id);
            create index on materialized_finalriskofbiasscore (score_id);
            create index on materialized_finalriskofbiasscore (study_id);
            """,
            """
            drop materialized view materialized_finalriskofbiasscore;
            """,
        )
    ]
