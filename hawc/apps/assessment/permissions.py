from typing import TYPE_CHECKING, Self

from django.core.cache import cache
from pydantic import BaseModel

from ..common.helper import cacheable

if TYPE_CHECKING:
    from ..myuser.models import HAWCUser
    from ..study.models import Study


class AssessmentPermissions(BaseModel):
    public: bool
    editable: bool
    project_manager: set[int]
    team_members: set[int]
    reviewers: set[int]

    @classmethod
    def get_cache_key(cls, assessment_id: int) -> str:
        return f"assessment-perms-{assessment_id}"

    @classmethod
    def clear_cache(cls, assessment_id: int):
        key = cls.get_cache_key(assessment_id)
        cache.delete(key)

    @classmethod
    def get(cls, assessment) -> Self:
        key = cls.get_cache_key(assessment.id)

        def get_perms() -> Self:
            return cls(
                public=(assessment.public_on is not None),
                editable=assessment.editable,
                project_manager={user.id for user in assessment.project_manager.all()},
                team_members={user.id for user in assessment.team_members.all()},
                reviewers={user.id for user in assessment.reviewers.all()},
            )

        perms = cacheable(get_perms, key)
        return perms

    def project_manager_or_higher(self, user: HAWCUser) -> bool:
        """
        Check if user is superuser or project-manager
        """
        if user.is_superuser:
            return True
        elif user.is_anonymous:
            return False
        else:
            return user.pk in self.project_manager

    def team_member_or_higher(self, user: HAWCUser) -> bool:
        """
        Check if person is superuser, project manager, or team member
        """
        if user.is_superuser:
            return True
        elif user.is_anonymous:
            return False
        else:
            return user.pk in self.project_manager or user.pk in self.team_members

    def reviewer_or_higher(self, user: HAWCUser) -> bool:
        """
        If person is superuser, project manager, team member, or reviewer
        """
        if user.is_superuser:
            return True
        elif user.is_anonymous:
            return False
        else:
            return (
                user.pk in self.project_manager
                or user.pk in self.team_members
                or user.pk in self.reviewers
            )

    def can_edit_object(self, user: HAWCUser) -> bool:
        """
        If person has enhanced permissions beyond the general public, which may
        be used to view attachments associated with a study.
        """
        if user.is_superuser:
            return True
        return self.editable and self.team_member_or_higher(user)

    def can_view_object(self, user: HAWCUser) -> bool:
        """
        Superusers can view all, noneditible reviews can be viewed, team
        members or project managers can view.
        Anonymous users on noneditable projects cannot view, nor can those who
        are non members of a project.
        """
        if self.public:
            return True
        return self.reviewer_or_higher(user)

    def can_edit_study(self, study: Study, user: HAWCUser) -> bool:
        """
        Check if user can edit a study; dependent on if study is editable
        """
        return self.project_manager_or_higher(user) or (
            study.editable and self.can_edit_object(user)
        )

    def can_view_study(self, study: Study, user: HAWCUser) -> bool:
        """
        Check if user can view a study object; dependent on if a study is published
        """
        return self.can_edit_object(user) or (study.published and self.can_view_object(user))

    def to_dict(self, user, study=None):
        return {
            "view": self.can_view_study(study, user) if study else self.can_view_object(user),
            "edit": self.can_edit_study(study, user) if study else self.can_edit_object(user),
            "edit_assessment": self.project_manager_or_higher(user),
        }
