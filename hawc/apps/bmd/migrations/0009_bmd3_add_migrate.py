from django.db import migrations, models


def _get_selected_model_dict(Session, SelectedModel) -> dict:
    sm_dict = {}
    for sm in SelectedModel.objects.select_related("model"):
        if sm.model:
            # if we have a model, we know the related bmd session
            key = sm.model.session_id
        else:
            # if we dont have a model, we need to find the related session
            # get latest session which was executed successfully
            latest_session = (
                Session.objects.filter(
                    endpoint_id=sm.endpoint_id,
                    dose_units_id=sm.dose_units_id,
                    date_executed__isnull=False,
                )
                .order_by("-last_updated")
                .first()
            )
            if latest_session is None:
                # get latest session, regardless of execution status
                latest_session = (
                    Session.objects.filter(
                        endpoint_id=sm.endpoint_id, dose_units_id=sm.dose_units_id
                    )
                    .order_by("-last_updated")
                    .first()
                )
            key = latest_session.id
        sm_dict[key] = sm
    return sm_dict


def _migrate_session(sm_dict, Session):
    for session in Session.objects.prefetch_related("models").order_by("id"):
        selected = sm_dict.get(session.id)
        sess_models = []
        for model in session.models.all():
            model_serialized = dict(
                id=model.id,
                model_index=model.model_id,
                bmr_index=model.bmr_id,
                name=model.name,
                overrides=model.overrides,
                execution_error=model.execution_error,
                dfile=model.dfile,
                outfile=model.outfile,
                output=model.output,
            )
            sess_models.append(model_serialized)
        sess_models = sorted(sess_models, key=lambda model: model["id"])
        if isinstance(session.inputs, list):
            session.inputs = dict(version=1, bmrs=session.inputs)
        session.outputs = dict(models=sess_models)
        if selected:
            session.active = True
            session.selected = dict(
                version=1,
                model_id=selected.model_id,
                name=selected.model.name if selected.model else None,
                bmd=selected.model.output["BMD"] if selected.model else None,
                bmdl=selected.model.output["BMDL"] if selected.model else None,
                bmdu=selected.model.output["BMDU"] if selected.model else None,
                notes=selected.notes,
            )
        session.save()


def _check_active(Session, SelectedModel):
    n_sess = Session.objects.filter(active=True).count()
    n_selected = SelectedModel.objects.count()
    if n_sess != n_selected:
        raise ValueError(f"Active Session {n_sess} != SelectedModel {n_selected}")

    matches = {}
    for sess in Session.objects.filter(active=True):
        key = (sess.endpoint_id, sess.dose_units_id)
        if key in matches:
            raise ValueError(sess.id, matches[key].id)
        matches[key] = sess


def run_fwd(apps, schema_editor):
    SelectedModel = apps.get_model("bmd", "SelectedModel")
    Session = apps.get_model("bmd", "Session")
    sm_dict = _get_selected_model_dict(Session, SelectedModel)
    _migrate_session(sm_dict, Session)
    _check_active(Session, SelectedModel)


class Migration(migrations.Migration):
    dependencies = [
        ("bmd", "0008_add_bmds330"),
    ]

    operations = [
        migrations.AlterField(
            model_name="session",
            name="bmrs",
            field=models.JSONField(default=dict),
        ),
        migrations.RenameField(
            model_name="session",
            old_name="bmrs",
            new_name="inputs",
        ),
        migrations.AddField(
            model_name="session",
            name="active",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="session",
            name="outputs",
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name="session",
            name="errors",
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name="session",
            name="selected",
            field=models.JSONField(default=dict),
        ),
        migrations.RunPython(run_fwd, reverse_code=migrations.RunPython.noop),
    ]
