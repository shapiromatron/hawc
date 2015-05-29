from study.models import Study
from utils.helper import FlatFileExporter
from . import models

from copy import copy


class EndpointFlatComplete(FlatFileExporter):
    """
    Returns a complete export of all data required to rebuild the the
    animal bioassay study type from scratch.
    """

    def _get_header_row(self):
        self.doses = models.DoseUnits.doses_in_assessment(self.kwargs.get('assessment'))

        header = []
        header.extend(Study.flat_complete_header_row())
        header.extend(models.Experiment.flat_complete_header_row())
        header.extend(models.AnimalGroup.flat_complete_header_row())
        header.extend(models.DosingRegime.flat_complete_header_row())
        header.extend(models.Endpoint.flat_complete_header_row())
        header.extend([u'doses-{}'.format(d) for d in self.doses])
        header.extend(models.EndpointGroup.flat_complete_header_row())
        return header

    def _get_data_rows(self):
        rows = []
        for obj in self.queryset:
            ser = obj.get_json(json_encode=False)
            row = []
            row.extend(Study.flat_complete_data_row(ser['animal_group']['experiment']['study']))
            row.extend(models.Experiment.flat_complete_data_row(ser['animal_group']['experiment']))
            row.extend(models.AnimalGroup.flat_complete_data_row(ser['animal_group']))
            row.extend(models.DosingRegime.flat_complete_data_row(ser['animal_group']['dosing_regime']))
            row.extend(models.Endpoint.flat_complete_data_row(ser))
            for i, eg in enumerate(ser['endpoint_group']):
                row_copy = copy(row)
                row_copy.extend(models.DoseGroup.flat_complete_data_row(
                    ser['animal_group']['dosing_regime']['doses'],
                    self.doses, i))
                row_copy.extend(models.EndpointGroup.flat_complete_data_row(eg, ser))
                rows.append(row_copy)

        return rows


class EndpointFlatDataPivot(FlatFileExporter):
    """
    Return a subset of frequently-used data for generation of data-pivot
    visualizations.
    """

    def _get_header_row(self):
        return [
            'study',
            'study_url',
            'Study HAWC ID',
            'Study Published',

            'Experiment ID',
            'experiment',
            'experiment_url',
            'chemical',

            'Animal Group ID',
            'animal_group',
            'animal_group_url',
            'lifestage exposed',
            'lifestage assessed',
            'species strain',
            'generation',
            'animal description',
            'animal description (with N)',
            'sex',
            'route',
            'treatment period',

            'endpoint_name',
            'endpoint_url',
            'system',
            'organ',
            'effect',
            'tags',
            'observation_time',
            'data_type',
            'doses',
            'dose_units',
            'response_units',
            'Endpoint Key',

            'low_dose',
            'NOEL',
            'LOEL',
            'FEL',
            'high_dose',

            'BMD model name',
            'BMDL',
            'BMD',
            'BMDU',
            'CSF',

            'Row Key',
            'dose_index',
            'dose',
            'n',
            'incidence',
            'response',
            'stdev',
            'percentControlMean',
            'percentControlLow',
            'percentControlHigh'
        ]

    def _get_data_rows(self):

        units = self.kwargs.get('dose', None)

        def get_doses_list(ser):
            # compact the dose-list to only one set of dose-units; using the
            # selected dose-units if specified, else others
            if units:
                units_id = units.id
            else:
                units_id = ser['animal_group']['dosing_regime']['doses'][0]['dose_units']['id']
            return [
                d for d in ser['animal_group']['dosing_regime']['doses']
                if units_id == d['dose_units']['id']
            ]

        def get_dose_units(doses):
            return doses[0]['dose_units']['units']

        def get_doses_str(doses):
            values = u', '.join([str(float(d['dose'])) for d in doses])
            return u"{0} {1}".format(values, get_dose_units(doses))

        def get_dose(doses, idx):
            for dose in doses:
                if dose['dose_group_id'] == idx:
                    return float(dose['dose'])
            return None

        def get_species_strain(e):
            return u"{} {}".format(
                e['animal_group']['species'],
                e['animal_group']['strain']
            )

        def get_gen_species_strain_sex(e, withN=False):

            gen = e['animal_group']['generation']
            if len(gen) > 0:
                gen += " "

            ns_txt = ""
            if withN:
                ns = [eg["n"] for eg in e["endpoint_group"]]
                ns_txt = " " + models.EndpointGroup.getNRangeText(ns)

            return u"{}{}, {} ({}{})".format(
                gen,
                e['animal_group']['species'],
                e['animal_group']['strain'],
                e['animal_group']['sex_symbol'],
                ns_txt
            )

        def get_observation_time(e):
            txt = ""
            if e["observation_time"]:
                if e["observation_time"] % 1 == 0:
                    txt = u"{} {}".format(
                            int(e["observation_time"]),
                            e["observation_time_units"])
                else:
                    txt = u"{} {}".format(
                            e["observation_time"],
                            e["observation_time_units"])
            return txt

        def get_tags(e):
            effs = [tag["name"] for tag in e["effects"]]
            if len(effs) > 0:
                return u"|{0}|".format(u"|".join(effs))
            return ""

        def get_treatment_period(exp, dr):
            txt = exp["type"].lower()
            if txt.find("(") >= 0:
                txt = txt[:txt.find("(")]

            if dr["duration_exposure_text"]:
                txt = u"{0} ({1})".format(txt, dr["duration_exposure_text"])

            return txt

        rows = []
        for obj in self.queryset:
            ser = obj.get_json(json_encode=False)
            doses = get_doses_list(ser)

            # build endpoint-group independent data
            row = [
                ser['animal_group']['experiment']['study']['short_citation'],
                ser['animal_group']['experiment']['study']['url'],
                ser['animal_group']['experiment']['study']['id'],
                ser['animal_group']['experiment']['study']['published'],

                ser['animal_group']['experiment']['id'],
                ser['animal_group']['experiment']['name'],
                ser['animal_group']['experiment']['url'],
                ser['animal_group']['experiment']['chemical'],

                ser['animal_group']['id'],
                ser['animal_group']['name'],
                ser['animal_group']['url'],
                ser['animal_group']['lifestage_exposed'],
                ser['animal_group']['lifestage_assessed'],
                get_species_strain(ser),
                ser['animal_group']['generation'],
                get_gen_species_strain_sex(ser, withN=False),
                get_gen_species_strain_sex(ser, withN=True),
                ser['animal_group']['sex'],
                ser['animal_group']['dosing_regime']['route_of_exposure'].lower(),
                get_treatment_period(ser['animal_group']['experiment'],
                                     ser['animal_group']['dosing_regime']),

                ser['name'],
                ser['url'],
                ser['system'],
                ser['organ'],
                ser['effect'],
                get_tags(ser),
                get_observation_time(ser),
                ser['data_type_label'],
                get_doses_str(doses),
                get_dose_units(doses),
                ser['response_units'],
                ser['id']
            ]

            # dose-group specific information
            if len(ser['endpoint_group']) > 1:
                row.extend([
                    get_dose(doses, 1),  # first non-zero dose
                    get_dose(doses, ser['NOEL']),
                    get_dose(doses, ser['LOEL']),
                    get_dose(doses, ser['FEL']),
                    get_dose(doses, len(ser['endpoint_group'])-1),
                ])
            else:
                row.extend([None]*5)

            # BMD information
            if ser['BMD'] and units and ser['BMD'].get('outputs')\
                    and ser['BMD']['dose_units_id'] == units.id:
                row.extend([
                    ser['BMD']['outputs']['model_name'],
                    ser['BMD']['outputs']['BMDL'],
                    ser['BMD']['outputs']['BMD'],
                    ser['BMD']['outputs']['BMDU'],
                    ser['BMD']['outputs']['CSF']
                ])
            else:
                row.extend([None]*5)

            # endpoint-group information
            for i, eg in enumerate(ser['endpoint_group']):
                row_copy = copy(row)
                row_copy.extend([
                    eg['id'],
                    eg['dose_group_id'],
                    get_dose(doses, i),
                    eg['n'],
                    eg['incidence'],
                    eg['response'],
                    eg['stdev'],
                    eg['percentControlMean'],
                    eg['percentControlLow'],
                    eg['percentControlHigh']
                ])
                rows.append(row_copy)

        return rows
