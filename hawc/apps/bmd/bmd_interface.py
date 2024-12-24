import pybmds
from django.utils import timezone
from django.utils.text import slugify
from pybmds.datasets.base import DatasetBase
from pybmds.reporting.styling import Report

from ...tools import word
from ..animal.constants import DataType
from ..animal.models import Endpoint
from ..common.helper import ReportExport


def version():
    return pybmds.__version__


def build_dataset(endpoint: Endpoint, dose_units_id: int, n_drop_doses: int = 0) -> DatasetBase:
    ds = endpoint.get_json(json_encode=False)
    doses = [
        dose["dose"]
        for dose in ds["animal_group"]["dosing_regime"]["doses"]
        if dose["dose_units"]["id"] == dose_units_id
    ]
    grps = ds["groups"]

    # only get doses where data are reported
    doses = [d for d, grp in zip(doses, grps, strict=True) if grp["isReported"]]

    if endpoint.data_type == DataType.CONTINUOUS:
        Cls = pybmds.ContinuousDataset
        kwargs = dict(
            doses=doses,
            ns=[d["n"] for d in grps if d["isReported"]],
            means=[d["response"] for d in grps if d["isReported"]],
            stdevs=[d["stdev"] for d in grps if d["isReported"]],
        )
    elif endpoint.data_type in [DataType.DICHOTOMOUS, DataType.DICHOTOMOUS_CANCER]:
        Cls = pybmds.DichotomousDataset
        kwargs = dict(
            doses=doses,
            ns=[d["n"] for d in grps if d["isReported"]],
            incidences=[d["incidence"] for d in grps if d["isReported"]],
        )
    else:
        raise ValueError(f"Cannot create BMDS dataset for this data type: {endpoint.data_type}")

    # drop doses from the top
    for _i in range(n_drop_doses):
        [lst.pop() for lst in kwargs.values()]

    return Cls(**kwargs)


def build_session(dataset) -> pybmds.Session:
    return pybmds.Session(dataset=dataset)


def build_and_execute(endpoint, inputs):
    dataset = build_dataset(
        endpoint, inputs.settings.dose_units_id, inputs.settings.num_doses_dropped
    )
    session = build_session(dataset)
    inputs.add_models(session)
    session.execute_and_recommend()
    return session


def create_report(session: pybmds.Session, name: str, url: str, versions: dict) -> ReportExport:
    report = Report.build_default()
    report.document.add_heading(name, 1)
    # add report generation timestamp
    timestamp = timezone.now().strftime("%Y-%b-%d %H:%m %Z")
    word.write_setting_p(report.document, "Report Generated: ", timestamp)
    # add URL to analysis
    p = report.document.add_paragraph()
    p.add_run("Analysis URL: ").bold = True
    word.add_url_hyperlink(p, url, "View")
    # add pybmds version information
    version_str = f"pybmds {versions['python']}; bmdscore {versions['dll']}"
    word.write_setting_p(report.document, "BMDS Version: ", version_str)
    # add report data
    report = session.to_docx(report=report, header_level=1, all_models=True)
    return ReportExport(docx=report, filename=slugify(name))
