from collections import Counter

import pytest

from hawc.apps.animal import models


@pytest.mark.django_db
class TestChangeNumDoseGroups:
    dr_id = 3

    def test_addition(self):
        # assert that adding a dose-group creates endpoint groups

        dose_regime = models.DosingRegime.objects.get(id=self.dr_id)
        assert dose_regime.num_dose_groups == 5

        assert set(
            models.DoseGroup.objects.filter(dose_regime=self.dr_id).values_list(
                "dose_group_id", flat=True
            )
        ) == {0, 1, 2, 3, 4}
        egs = models.EndpointGroup.objects.filter(endpoint__animal_group__dosing_regime=self.dr_id)
        assert Counter(eg.dose_group_id for eg in egs) == {0: 5, 1: 5, 2: 5, 3: 5, 4: 5}

        dose_regime.num_dose_groups = 6
        dose_regime.save()

        egs = models.EndpointGroup.objects.filter(endpoint__animal_group__dosing_regime=self.dr_id)
        assert Counter(eg.dose_group_id for eg in egs) == {0: 5, 1: 5, 2: 5, 3: 5, 4: 5, 5: 5}

    def test_deletion(self):
        # assert that deleting a dose-group removes endpoint groups

        dose_regime = models.DosingRegime.objects.get(id=self.dr_id)
        assert dose_regime.num_dose_groups == 5

        assert set(
            models.DoseGroup.objects.filter(dose_regime=self.dr_id).values_list(
                "dose_group_id", flat=True
            )
        ) == {0, 1, 2, 3, 4}
        egs = models.EndpointGroup.objects.filter(endpoint__animal_group__dosing_regime=self.dr_id)
        assert Counter(eg.dose_group_id for eg in egs) == {0: 5, 1: 5, 2: 5, 3: 5, 4: 5}

        dose_regime.num_dose_groups = 4
        dose_regime.save()

        egs = models.EndpointGroup.objects.filter(endpoint__animal_group__dosing_regime=self.dr_id)
        assert Counter(eg.dose_group_id for eg in egs) == {0: 5, 1: 5, 2: 5, 3: 5}
