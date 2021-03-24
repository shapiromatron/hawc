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
                ROW_NUMBER() OVER (ORDER BY score_id, c.model, so.object_id) as id,
                s.id as "score_id",
                s.score as "score_score",
                s.is_default,
                r.study_id,
                s.metric_id,
                s.riskofbias_id,
                c.app_label,
                c.model,
                so.object_id
            from riskofbias_riskofbiasscore s
            left join riskofbias_riskofbias r
            on s.riskofbias_id = r.id
            left join riskofbias_riskofbiasscoreoverrideobject so
            on s.id = so.score_id
            left join django_content_type c
            on so.content_type_id = c.id
            where r.final and r.active;
            create unique index on materialized_score (id);
            create index on materialized_score (score_id);
            create index on materialized_score (study_id);
            """,
            """
            drop materialized view materialized_score;
            """,
        )
    ]
