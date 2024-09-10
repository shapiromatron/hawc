import {ehvFields} from "animal/EndpointForm/constants";
import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import HelpTextPopup from "shared/components/HelpTextPopup";
import h from "shared/utils/helpers";

const MAX_ROWS = 150;

@inject("store")
@observer
class Table extends Component {
    render() {
        const {filteredDataset, query} = this.props.store,
            regex = query.length > 0 ? new RegExp(h.escapeRegexString(query), "gi") : null,
            helpText = ehvFields.helpText,
            highlightedSpan = text => {
                return regex ? (
                    <span
                        dangerouslySetInnerHTML={{
                            __html: text.replace(regex, match => `<mark>${match}</mark>`),
                        }}
                    />
                ) : (
                    text
                );
            };

        return (
            <>
                <p>
                    <b>{filteredDataset.length}</b> items found.&nbsp;
                    {filteredDataset.length === 0 ? "Please try a different search string." : ""}
                    {filteredDataset.length > MAX_ROWS ? `Showing the first ${MAX_ROWS} rows.` : ""}
                </p>
                {filteredDataset.length > 0 ? (
                    <table className="table table-sm table-striped">
                        <colgroup>
                            <col width="20%" />
                            <col width="20%" />
                            <col width="20%" />
                            <col width="20%" />
                            <col width="20%" />
                        </colgroup>
                        <thead>
                            <tr>
                                <th>
                                    System
                                    <HelpTextPopup title="System" content={helpText.system_popup} />
                                </th>
                                <th>
                                    Organ
                                    <HelpTextPopup title="Organ" content={helpText.organ_popup} />
                                </th>
                                <th>
                                    Effect
                                    <HelpTextPopup title="Effect" content={helpText.effect_popup} />
                                </th>
                                <th>
                                    Effect subtype
                                    <HelpTextPopup
                                        title="Effect subtype"
                                        content={helpText.effect_subtype_popup}
                                    />
                                </th>
                                <th>
                                    Endpoint/Outcome
                                    <HelpTextPopup
                                        title="Endpoint/Outcome"
                                        content={helpText.endpoint_name_popup}
                                    />
                                </th>
                            </tr>
                        </thead>
                        <tbody>
                            {filteredDataset.slice(0, MAX_ROWS).map(d => (
                                <tr key={d._key}>
                                    <td>
                                        <span className="badge badge-light">
                                            {d.system_term_id}
                                        </span>
                                        &nbsp;
                                        {highlightedSpan(d.system)}
                                    </td>
                                    <td>
                                        <span className="badge badge-light">{d.organ_term_id}</span>
                                        &nbsp;
                                        {highlightedSpan(d.organ)}
                                    </td>
                                    <td>
                                        <span className="badge badge-light">
                                            {d.effect_term_id}
                                        </span>
                                        &nbsp;
                                        {highlightedSpan(d.effect)}
                                    </td>
                                    <td>
                                        <span className="badge badge-light">
                                            {d.effect_subtype_term_id}
                                        </span>
                                        &nbsp;
                                        {highlightedSpan(d.effect_subtype)}
                                    </td>
                                    <td>
                                        <span className="badge badge-light">{d.name_term_id}</span>
                                        &nbsp;
                                        {highlightedSpan(d.name)}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                ) : null}
            </>
        );
    }
}
Table.propTypes = {
    store: PropTypes.object,
};

export default Table;
