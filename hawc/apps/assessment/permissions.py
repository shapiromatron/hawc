from typing import Set

from django.conf import settings
from django.core.cache import cache
from pydantic import BaseModel


class AssessmentPermissions(BaseModel):
    public: bool
    editable: bool
    project_manager: Set[int]
    team_members: Set[int]
    reviewers: Set[int]

    @classmethod
    def get_cache_key(cls, assessment_id: int) -> str:
        return f"assessment-perms-{assessment_id}"

    @classmethod
    def clear_cache(cls, assessment_id: int):
        key = cls.get_cache_key(assessment_id)
        cache.delete(key)

    @classmethod
    def get(cls, assessment) -> "AssessmentPermissions":
        key = cls.get_cache_key(assessment.id)
        perms = cache.get(key)
        if perms is None:
            perms = cls(
                public=assessment.public,
                editable=assessment.editable,
                project_manager={user.id for user in assessment.project_manager.all()},
                team_members={user.id for user in assessment.team_members.all()},
                reviewers={user.id for user in assessment.reviewers.all()},
            )
            cache.set(key, perms, settings.CACHE_1_HR)
        return perms

    def can_view_object(self, user) -> bool:
        """
        Superusers can view all, noneditible reviews can be viewed, team
        members or project managers can view.
        Anonymous users on noneditable projects cannot view, nor can those who
        are non members of a project.
        """
        if self.public:
            return True
        return self.part_of_team(user)

    def can_edit_object(self, user) -> bool:
        """
        If person has enhanced permissions beyond the general public, which may
        be used to view attachments associated with a study.
        """
        if user.is_superuser:
            return True
        elif user.is_anonymous:
            return False
        else:
            return self.editable and (
                user.id in self.project_manager or user.id in self.team_members
            )

    def can_edit_assessment(self, user) -> bool:
        """
        If person is superuser or assessment is editible and user is a project
        manager or team member.
        """
        if user.is_superuser:
            return True
        elif user.is_anonymous:
            return False
        else:
            return user.id in self.project_manager

    def part_of_team(self, user) -> bool:
        """
        Used for permissions-checking if attachments for a study can be
        viewed. Checks to ensure user is part of the team.
        """
        if user.is_superuser:
            return True
        elif user.is_anonymous:
            return False
        else:
            return (
                user.id in self.project_manager
                or user.id in self.team_members
                or user.id in self.reviewers
            )

    def team_member_or_higher(self, user) -> bool:
        """
        Check if user is superuser, project-manager, or team-member, otherwise False.
        """
        if user.is_superuser:
            return True
        elif user.is_anonymous:
            return False
        else:
            return user.id in self.project_manager or user.id in self.team_members

    def can_edit_study(self, study, user) -> bool:
        """
        Check if user can edit a study; dependent on if study is editable
        """
        if study.editable and self.can_edit_object(user):
            return True

        return self.can_edit_assessment(user)
