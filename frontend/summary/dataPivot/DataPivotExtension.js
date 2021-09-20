import _ from "lodash";
import React, {Component, Fragment} from "react";
import ReactDOM from "react-dom";

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
            headers = new Set(dp.data[0]).keys();
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
            _dpe_option_txt: "Show animal experiment",
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
            _dpe_option_txt: "Show animal endpoint (basic)",
            _dpe_options: {
                complete: false,
            },
            hasModal: true,
        },
        {
            _dpe_name: "endpoint_complete",
            _dpe_key: "endpoint id",
            _dpe_cls: Endpoint,
            _dpe_option_txt: "Show animal endpoint (complete)",
            _dpe_options: {
                complete: true,
            },
            hasModal: true,
        },
        {
            _dpe_name: "study_population",
            _dpe_key: "study population id",
            _dpe_cls: StudyPopulation,
            _dpe_option_txt: "Show epi study population",
            hasModal: true,
        },
        {
            _dpe_name: "comparison_set",
            _dpe_key: "comparison set id",
            _dpe_cls: ComparisonSet,
            _dpe_option_txt: "Show epi comparison set",
            hasModal: true,
        },
        {
            _dpe_name: "exposure",
            _dpe_key: "exposure id",
            _dpe_cls: Exposure,
            _dpe_option_txt: "Show epi exposure",
            hasModal: true,
        },
        {
            _dpe_name: "outcome",
            _dpe_key: "outcome id",
            _dpe_cls: Outcome,
            _dpe_option_txt: "Show epi outcome",
            hasModal: true,
        },
        {
            _dpe_name: "result",
            _dpe_key: "result id",
            _dpe_cls: Result,
            _dpe_option_txt: "Show epi result",
            hasModal: true,
        },
        {
            _dpe_name: "meta_protocol",
            _dpe_key: "protocol id",
            _dpe_cls: MetaProtocol,
            _dpe_option_txt: "Show epi meta protocol",
            hasModal: true,
        },
        {
            _dpe_name: "meta_result",
            _dpe_key: "meta result id",
            _dpe_cls: MetaResult,
            _dpe_option_txt: "Show epi meta result",
            hasModal: true,
        },
        {
            _dpe_name: "iv_chemical",
            _dpe_key: "chemical id",
            _dpe_cls: IVChemical,
            _dpe_option_txt: "Show invitro chemical",
            hasModal: true,
        },
        {
            _dpe_name: "iv_experiment",
            _dpe_key: "IVExperiment id",
            _dpe_cls: IVExperiment,
            _dpe_option_txt: "Show invitro experiment",
            hasModal: true,
        },
        {
            _dpe_name: "iv_celltype",
            _dpe_key: "IVCellType id",
            _dpe_cls: IVCellType,
            _dpe_option_txt: "Show invitro cell type",
            hasModal: true,
        },
        {
            _dpe_name: "iv_endpoint",
            _dpe_key: "IVEndpoint id",
            _dpe_cls: IVEndpoint,
            _dpe_option_txt: "Show invitro endpoint",
            hasModal: true,
        },
    ],
});

class ExtensionTable extends Component {
    render() {
        const columns = DataPivotExtension.extByColumnKey();
        return (
            <table className="table table-sm table-bordered">
                <thead>
                    <tr>
                        <th>Input column header*</th>
                        <th>Available action(s)</th>
                    </tr>
                </thead>
                <tbody>
                    {_.map(columns, (arr, col) => (
                        <tr key={col}>
                            <td>{col}</td>
                            <td>
                                <ul className={arr.length == 1 ? "list-unstyled mb-0" : "mb-0"}>
                                    {arr.map((d, i) => (
                                        <li key={i}>{d._dpe_option_txt}</li>
                                    ))}
                                </ul>
                            </td>
                        </tr>
                    ))}
                </tbody>
                <tfoot>
                    <tr>
                        <td colSpan={2}>
                            * Column header names are case sensitive. User permissions are checked
                            whenever a user attempts to access any resource in HAWC, so you must use
                            the correct HAWC IDs to enable these interactive features.
                        </td>
                    </tr>
                </tfoot>
            </table>
        );
    }
}

function renderExtensionTable(el) {
    ReactDOM.render(<ExtensionTable />, el);
}

export default DataPivotExtension;
export {ExtensionTable, renderExtensionTable};
