from django.urls import reverse
from pydantic import BaseModel


class Breadcrumb(BaseModel):
    name: str
    url: str | None = None

    @classmethod
    def build_root(cls, user) -> "Breadcrumb":
        if user.is_authenticated:
            return Breadcrumb(name="Home", url=reverse("portal"))
        else:
            return Breadcrumb(name="Public Assessments", url=reverse("assessment:public_list"))

    @classmethod
    def from_object(cls, obj) -> "Breadcrumb":
        """Return a single breadcrumb from one object.

        Args:
            obj: A model instance with a `get_absolute_url()` method

        Returns:
            A Breadcrumb object
        """
        return cls(name=str(obj), url=obj.get_absolute_url())

    @classmethod
    def build_assessment_crumbs(cls, user, obj) -> list["Breadcrumb"]:
        """
        Recursively get a list of breadcrumb objects from current object to assessment root.

        Each parent request may require an additional database query.

        Args:
            obj: a model instance related to an assessment.

        Returns:
            list[Breadcrumb]: A list of crumbs; with assessment first
        """
        crumbs = []
        while True:
            crumbs.append(cls.from_object(obj))
            parent_key = obj.BREADCRUMB_PARENT
            if parent_key is None:
                break
            obj = getattr(obj, parent_key)

        crumbs.append(cls.build_root(user))
        return crumbs[::-1]

    @classmethod
    def build_crumbs(
        cls, user, name: str, extras: list["Breadcrumb"] | None = None
    ) -> list["Breadcrumb"]:
        """
        Build crumbs where there is not an assessment root.

        Args:
            user: the django request user
            name: the final breadcrumb text
            extras: (optional) intermediate crumbs between the root and final

        Returns:
            Returns a list of breadcrumbs
        """
        crumbs = [cls.build_root(user)]
        if extras:
            crumbs.extend(extras)
        crumbs.append(Breadcrumb(name=name))
        return crumbs
