import _ from "lodash";
import * as d3 from "d3";

import Reference from "lit/Reference";

import Study from "study/Study";

import Experiment from "animal/Experiment";
import AnimalGroup from "animal/AnimalGroup";
import Endpoint from "animal/Endpoint";

import StudyPopulation from "epi/StudyPopulation";
import ComparisonSet from "epi/ComparisonSet";
import Exposure from "epi/Exposure";
import Outcome from "epi/Outcome";
import Result from "epi/Result";

import MetaProtocol from "epimeta/MetaProtocol";
import MetaResult from "epimeta/MetaResult";

import IVChemical from "invitro/IVChemical";
import IVExperiment from "invitro/IVExperiment";
import IVCellType from "invitro/IVCellType";
import IVEndpoint from "invitro/IVEndpoint";

import {NULL_CASE} from "./shared";

class DataPivotExtension {
    static extByName() {
        return _.keyBy(DataPivotExtension.values, "_dpe_name");
    }

    static extByColumnKey() {
        return _.groupBy(DataPivotExtension.values, "_dpe_key");
    }

    static update_extensions(obj, key) {
        var dpe_keys = DataPivotExtension.extByName(),
            match = dpe_keys[key];
        if (match) {
            _.extend(obj, match);
        } else {
            console.error(`Unrecognized DPE key: ${key}`);
        }
    }

    static get_options(dp) {
        // extension options dependent on available data-columns
        var build_opt = function(val, txt) {
                return `<option value="${val}">${txt}</option>`;
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

    get_detail_url(settings, datarow) {
        return settings._dpe_cls.get_detail_url(datarow[settings._dpe_key], settings._dpe_name);
    }
}

_.extend(DataPivotExtension, {
    values: [
        {
            _dpe_name: "reference",
            _dpe_key: "reference id",
            _dpe_cls: Reference,
            _dpe_option_txt: "Show reference",
            hasModal: false,
        },
        {
            _dpe_name: "hero",
            _dpe_key: "hero id",
            _dpe_cls: Reference,
            _dpe_option_txt: "Show HERO",
            hasModal: false,
        },
        {
            _dpe_name: "pubmed",
            _dpe_key: "pubmed id",
            _dpe_cls: Reference,
            _dpe_option_txt: "Show PubMed",
            hasModal: false,
        },
        {
            _dpe_name: "study",
            _dpe_key: "study id",
            _dpe_cls: Study,
            _dpe_option_txt: "Show study",
            hasModal: true,
        },
        {
            _dpe_name: "experiment",
            _dpe_key: "experiment id",
            _dpe_cls: Experiment,
            _dpe_option_txt: "Show experiment",
            hasModal: true,
        },
        {
            _dpe_name: "animal_group",
            _dpe_key: "animal group id",
            _dpe_cls: AnimalGroup,
            _dpe_option_txt: "Show animal group",
            hasModal: true,
        },
        {
            _dpe_name: "endpoint",
            _dpe_key: "endpoint id",
            _dpe_cls: Endpoint,
            _dpe_option_txt: "Show endpoint (basic)",
            _dpe_options: {
                complete: false,
            },
            hasModal: true,
        },
        {
            _dpe_name: "endpoint_complete",
            _dpe_key: "endpoint id",
            _dpe_cls: Endpoint,
            _dpe_option_txt: "Show endpoint (complete)",
            _dpe_options: {
                complete: true,
            },
            hasModal: true,
        },
        {
            _dpe_name: "study_population",
            _dpe_key: "study population id",
            _dpe_cls: StudyPopulation,
            _dpe_option_txt: "Show study population",
            hasModal: true,
        },
        {
            _dpe_name: "comparison_set",
            _dpe_key: "comparison set id",
            _dpe_cls: ComparisonSet,
            _dpe_option_txt: "Show comparison set",
            hasModal: true,
        },
        {
            _dpe_name: "exposure",
            _dpe_key: "exposure id",
            _dpe_cls: Exposure,
            _dpe_option_txt: "Show exposure",
            hasModal: true,
        },
        {
            _dpe_name: "outcome",
            _dpe_key: "outcome id",
            _dpe_cls: Outcome,
            _dpe_option_txt: "Show outcome",
            hasModal: true,
        },
        {
            _dpe_name: "result",
            _dpe_key: "result id",
            _dpe_cls: Result,
            _dpe_option_txt: "Show result",
            hasModal: true,
        },
        {
            _dpe_name: "meta_protocol",
            _dpe_key: "protocol id",
            _dpe_cls: MetaProtocol,
            _dpe_option_txt: "Show protocol",
            hasModal: true,
        },
        {
            _dpe_name: "meta_result",
            _dpe_key: "meta result id",
            _dpe_cls: MetaResult,
            _dpe_option_txt: "Show meta result",
            hasModal: true,
        },
        {
            _dpe_name: "iv_chemical",
            _dpe_key: "chemical id",
            _dpe_cls: IVChemical,
            _dpe_option_txt: "Show chemical",
            hasModal: true,
        },
        {
            _dpe_name: "iv_experiment",
            _dpe_key: "IVExperiment id",
            _dpe_cls: IVExperiment,
            _dpe_option_txt: "Show experiment",
            hasModal: true,
        },
        {
            _dpe_name: "iv_celltype",
            _dpe_key: "IVCellType id",
            _dpe_cls: IVCellType,
            _dpe_option_txt: "Show cell type",
            hasModal: true,
        },
        {
            _dpe_name: "iv_endpoint",
            _dpe_key: "IVEndpoint id",
            _dpe_cls: IVEndpoint,
            _dpe_option_txt: "Show endpoint",
            hasModal: true,
        },
    ],
});

export default DataPivotExtension;
