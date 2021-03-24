from django.db import migrations


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("materialized", "0001_initial"),
        ("animal", "0030_django31"),
    ]

    operations = [
        migrations.RunSQL(
            """
            create materialized view materialized_endpoint as

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

            create unique index on materialized_endpoint (id);
            create index on materialized_endpoint (assessment_id);
            """,
            """
            drop materialized view materialized_endpoint;
            """,
        )
    ]
