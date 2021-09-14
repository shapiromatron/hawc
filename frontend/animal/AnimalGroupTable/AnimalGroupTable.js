import $ from "$";
import _ from "lodash";
import React, {Component} from "react";
import PropTypes from "prop-types";
import {inject, observer} from "mobx-react";

import h from "shared/utils/helpers";

const nRow = (endpoint, index) => {
        return (
            <tr key={`n-${index}`} className="table-secondary">
                <td>N</td>
                <td>-</td>
                <td>-</td>
                {endpoint.data.groups.map((d, i) => (
                    <td key={i}>{d.n || "-"}</td>
                ))}
            </tr>
        );
    },
    renderEndpointRow = (store, endpoint) => {
        const {footnotes} = store,
            {id, url, name, groups, observation_time_text, organ, data_type} = endpoint.data;
        let dr_control, html, fn, response;
        return (
            <tr key={`e-${id}`}>
                <td>
                    <a href={url}>{name}</a>
                </td>
                <td>{organ}</td>
                <td>{observation_time_text}</td>
                {groups.map((v, i) => {
                    if (i === 0) {
                        dr_control = v;
                    }
                    if (!v.isReported) {
                        html = "-";
                    } else {
                        fn = endpoint.add_endpoint_group_footnotes(footnotes, i);
                        if (data_type === "C") {
                            if (_.isNumber(v.response) && _.isNumber(v.stdev)) {
                                response = `${h.ff(v.response)} ± ${h.ff(v.stdev)}`;
                            } else if (_.isNumber(v.response)) {
                                response = h.ff(v.response);
                            } else {
                                response = "-";
                            }
                            html = "";
                            if (i > 0 && _.isNumber(v.response) && dr_control.response > 0) {
                                html = endpoint._continuous_percent_difference_from_control(
                                    v,
                                    dr_control
                                );
                                html = html === "NR" ? "" : ` (${html}%)`;
                            }
                            html = `${response}${html}${fn}`;
                        } else if (data_type === "P") {
                            html = `${endpoint.get_pd_string(v)}${fn}`;
                        } else if (["D", "DC"].indexOf(data_type) >= 0) {
                            const percentChange = endpoint._dichotomous_percent_change_incidence(v),
                                fn = endpoint.add_endpoint_group_footnotes(footnotes, i);
                            html = `${v.incidence}/${v.n} (${percentChange}%)${fn}`;
                        } else {
                            console.error("unknown data-type");
                        }
                    }
                    return <td key={i} dangerouslySetInnerHTML={{__html: html}} />;
                })}
            </tr>
        );
    };

@inject("store")
@observer
class AnimalGroupTable extends Component {
    renderHeader() {
        const {doses, units, firstEndpoint, numCols} = this.props.store,
            colWidth = Math.round(100 / (numCols + 1));
        let doseUnitsHeader = `Dose [${units[0].name}]`;
        if (units.length > 1) {
            doseUnitsHeader += ` (${units
                .slice(1)
                .map(d => d.name)
                .join("; ")})`;
        }
        return (
            <thead>
                <tr>
                    <th
                        rowSpan={2}
                        width={`${colWidth * 2}%`}
                        className="sortable"
                        data-sortable-field="name">
                        Endpoint
                    </th>
                    <th
                        rowSpan={2}
                        width={`${colWidth}%`}
                        className="sortable"
                        data-sortable-field="organ">
                        Organ
                    </th>
                    <th
                        rowSpan={2}
                        width={`${colWidth}%`}
                        className="sortable"
                        data-sortable-field="obs-time">
                        Obs. time.
                    </th>
                    <th colSpan={doses.length} width={`${colWidth * doses.length}%`}>
                        {doseUnitsHeader}
                    </th>
                </tr>
                <tr>
                    {_.range(doses.length).map(idx => {
                        const doses = firstEndpoint.doseUnits.dosesByDoseIndex(idx);
                        let dosesHeader = `${h.ff(doses[0].dose)}`;
                        if (doses.length > 1) {
                            dosesHeader += ` (${doses
                                .slice(1)
                                .map(d => h.ff(d.dose))
                                .join("; ")})`;
                        }
                        return <th key={idx}>{dosesHeader}</th>;
                    })}
                </tr>
            </thead>
        );
    }
    renderBody() {
        const {store} = this.props,
            {endpointsByN} = store;
        return (
            <tbody>
                {endpointsByN.map((endpoints, index) => {
                    const rows = endpoints.map(e => renderEndpointRow(store, e));
                    rows.unshift(nRow(endpoints[0], index));
                    return rows;
                })}
            </tbody>
        );
    }
    renderFooter() {
        const {footnotes, numCols} = this.props.store,
            html = {__html: footnotes.html_list().join("<br>")};

        if (footnotes.footnotes.length === 0) {
            return null;
        }
        return (
            <tfoot>
                <tr>
                    <td colSpan={numCols} dangerouslySetInnerHTML={html} />
                </tr>
            </tfoot>
        );
    }
    render() {
        const {endpointsDr} = this.props.store;
        if (endpointsDr.length === 0) {
            return <p>No endpoints are available with dose-response data.</p>;
        }
        return (
            <table className="table table-condensed">
                {this.renderHeader()}
                {this.renderBody()}
                {this.renderFooter()}
            </table>
        );
    }
}
AnimalGroupTable.propTypes = {
    store: PropTypes.object,
};

export default AnimalGroupTable;
