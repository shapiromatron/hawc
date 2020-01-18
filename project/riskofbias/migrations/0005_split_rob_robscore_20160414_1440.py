# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-14 19:40


from django.db import migrations


def splitRobScore(apps, schema_editor):
    """
    For each study,
        get all old_robs,
        create new_rob,
        create rob_score from each old_rob, setting metric on score,
        then set rob_score->rob to new_rob.
    """
    RiskOfBias = apps.get_model("riskofbias", "RiskOfBias")
    RiskOfBiasScore = apps.get_model("riskofbias", "RiskOfBiasScore")
    Study = apps.get_model("study", "Study")
    for study in Study.objects.all():
        old_robs = list(study.qualities.all())
        new_rob = RiskOfBias.objects.create(study=study)
        for rob in old_robs:
            RiskOfBiasScore.objects.create(
                riskofbias=new_rob, metric=rob.metric, score=rob.score, notes=rob.notes,
            )
            rob.delete()


def revertRobScoreSplit(apps, schema_editor):
    RiskOfBias = apps.get_model("riskofbias", "RiskOfBias")
    RiskOfBiasScore = apps.get_model("riskofbias", "RiskOfBiasScore")
    for score in RiskOfBiasScore.objects.all():
        study = score.riskofbias.study
        RiskOfBias.objects.create(
            study=study,
            metric=score.metric,
            score=score.score,
            notes=score.notes,
            author=score.riskofbias.author,
            conflict_resolution=score.riskofbias.conflict_resolution,
        )
        score.delete()


class Migration(migrations.Migration):

    dependencies = [
        ("riskofbias", "0004_auto_20160413_1353"),
    ]

    operations = [migrations.RunPython(splitRobScore, reverse_code=revertRobScoreSplit)]
