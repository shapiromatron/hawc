import _ from 'lodash';
import d3 from 'd3';

import Study from 'study/Study';

import Experiment from 'animal/Experiment';
import AnimalGroup from 'animal/AnimalGroup';
import Endpoint from 'animal/Endpoint';

import StudyPopulation from 'epi/StudyPopulation';
import ComparisonSet from 'epi/ComparisonSet';
import Exposure from 'epi/Exposure';
import Outcome from 'epi/Outcome';
import Result from 'epi/Result';

import MetaProtocol from 'epimeta/MetaProtocol';
import MetaResult from 'epimeta/MetaResult';

import IVChemical from 'invitro/IVChemical';
import IVExperiment from 'invitro/IVExperiment';
import IVCellType from 'invitro/IVCellType';
import IVEndpoint from 'invitro/IVEndpoint';

import { NULL_CASE } from './shared';

class DataPivotExtension {
    static extByName() {
        return _.keyBy(DataPivotExtension.values, '_dpe_name');
    }

    static extByColumnKey() {
        return _.groupBy(DataPivotExtension.values, '_dpe_key');
    }

    static update_extensions(obj, key) {
        var dpe_keys = DataPivotExtension.extByName(),
            match = dpe_keys[key];
        if (match) {
            _.extend(obj, match);
        } else {
            console.log('Unrecognized DPE key: {0}'.printf(key));
        }
    }

    static get_options(dp) {
        // extension options dependent on available data-columns
        var build_opt = function(val, txt) {
                return '<option value="{0}">{1}</option>'.printf(val, txt);
            },
            opts = [build_opt(NULL_CASE, NULL_CASE)],
            headers;

        if (dp.data.length > 0) {
            headers = d3.set(d3.map(dp.data[0]).keys());
            _.each(DataPivotExtension.extByColumnKey(), function(vals, key) {
                if (headers.has(key)) {
                    opts.push.apply(
                        opts,
                        vals.map(function(d) {
                            return build_opt(d._dpe_name, d._dpe_option_txt);
                        })
                    );
                }
            });
        }
        return opts;
    }

    render_plottip(settings, datarow) {
        settings._dpe_cls.displayAsModal(datarow[settings._dpe_key], settings._dpe_options);
    }
}

_.extend(DataPivotExtension, {
    values: [
        {
            _dpe_name: 'study',
            _dpe_key: 'study id',
            _dpe_cls: Study,
            _dpe_option_txt: 'Show study',
        },
        {
            _dpe_name: 'experiment',
            _dpe_key: 'experiment id',
            _dpe_cls: Experiment,
            _dpe_option_txt: 'Show experiment',
        },
        {
            _dpe_name: 'animal_group',
            _dpe_key: 'animal group id',
            _dpe_cls: AnimalGroup,
            _dpe_option_txt: 'Show animal group',
        },
        {
            _dpe_name: 'endpoint',
            _dpe_key: 'endpoint id',
            _dpe_cls: Endpoint,
            _dpe_option_txt: 'Show endpoint (basic)',
            _dpe_options: {
                complete: false,
            },
        },
        {
            _dpe_name: 'endpoint_complete',
            _dpe_key: 'endpoint id',
            _dpe_cls: Endpoint,
            _dpe_option_txt: 'Show endpoint (complete)',
            _dpe_options: {
                complete: true,
            },
        },
        {
            _dpe_name: 'study_population',
            _dpe_key: 'study population id',
            _dpe_cls: StudyPopulation,
            _dpe_option_txt: 'Show study population',
        },
        {
            _dpe_name: 'comparison_set',
            _dpe_key: 'comparison set id',
            _dpe_cls: ComparisonSet,
            _dpe_option_txt: 'Show comparison set',
        },
        {
            _dpe_name: 'exposure',
            _dpe_key: 'exposure id',
            _dpe_cls: Exposure,
            _dpe_option_txt: 'Show exposure',
        },
        {
            _dpe_name: 'outcome',
            _dpe_key: 'outcome id',
            _dpe_cls: Outcome,
            _dpe_option_txt: 'Show outcome',
        },
        {
            _dpe_name: 'result',
            _dpe_key: 'result id',
            _dpe_cls: Result,
            _dpe_option_txt: 'Show result',
        },
        {
            _dpe_name: 'meta_protocol',
            _dpe_key: 'protocol id',
            _dpe_cls: MetaProtocol,
            _dpe_option_txt: 'Show protocol',
        },
        {
            _dpe_name: 'meta_result',
            _dpe_key: 'meta result id',
            _dpe_cls: MetaResult,
            _dpe_option_txt: 'Show meta result',
        },
        {
            _dpe_name: 'iv_chemical',
            _dpe_key: 'chemical id',
            _dpe_cls: IVChemical,
            _dpe_option_txt: 'Show chemical',
        },
        {
            _dpe_name: 'iv_experiment',
            _dpe_key: 'IVExperiment id',
            _dpe_cls: IVExperiment,
            _dpe_option_txt: 'Show experiment',
        },
        {
            _dpe_name: 'iv_celltype',
            _dpe_key: 'IVCellType id',
            _dpe_cls: IVCellType,
            _dpe_option_txt: 'Show cell type',
        },
        {
            _dpe_name: 'iv_endpoint',
            _dpe_key: 'IVEndpoint id',
            _dpe_cls: IVEndpoint,
            _dpe_option_txt: 'Show endpoint',
        },
    ],
});

export default DataPivotExtension;
