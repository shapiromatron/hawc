from django.db import migrations


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("riskofbias", "0022_new_rob_scores"),
    ]

    operations = [
        migrations.RunSQL(
            """
            create materialized view materialized_score as
            select
                ROW_NUMBER() OVER (ORDER BY scrs.score_id, scrs.model, scrs.object_id) as id,
                scrs.*,
                rob.study_id
            from (
                (select
                    scr.id as "score_id",
                    scr.score as "score_score",
                    scr.is_default,
                    scr.metric_id,
                    scr.riskofbias_id,
                    NULL as "app_label",
                    NULL as "model",
                    NULL as "object_id"
                from riskofbias_riskofbiasscore scr)
                union
                (select
                    scr.id as "score_id",
                    scr.score as "score_score",
                    scr.is_default,
                    scr.metric_id,
                    scr.riskofbias_id,
                    con.app_label,
                    con.model,
                    ovr.object_id
                from riskofbias_riskofbiasscore scr
                inner join riskofbias_riskofbiasscoreoverrideobject ovr
                on scr.id = ovr.score_id
                left join django_content_type con
                on ovr.content_type_id = con.id)
            ) scrs
            left join riskofbias_riskofbias rob
            on scrs.riskofbias_id = rob.id
            where rob.final and rob.active;
            create unique index on materialized_score (id);
            create index on materialized_score (score_id);
            create index on materialized_score (study_id);
            """,
            """
            drop materialized view materialized_score;
            """,
        )
    ]
