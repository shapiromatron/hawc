from django.db.models import TextChoices


class DurationGrouper(TextChoices):
    # values based on Trunc function
    # https://docs.djangoproject.com/en/3.2/ref/models/database-functions/#trunc
    annual = "year", "Annually"
    quarterly = "quarter", "Quarterly"
    monthly = "month", "Monthly"
    weekly = "week", "Weekly"
    daily = "day", "Daily"


class PandasDurationGrouper(TextChoices):
    annually = "YE", "Annually"
    quarterly = "QE", "Quarterly"
    monthly = "ME", "Monthly"
    weekly = "W", "Weekly"
    daily = "D", "Daily"


class GrowthModels(TextChoices):
    user = "user", "Users"
    assessment = "assessment", "Assessments"
    reference = "reference", "References"
    study = "study", "Studies"
    endpoint = "endpoint", "Endpoints"
    visual = "visual", "Visuals"
