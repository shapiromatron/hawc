import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import h from "shared/utils/helpers";

const MAX_ROWS = 150;

@inject("store")
@observer
class Table extends Component {
    render() {
        const {filteredDataset, query} = this.props.store,
            regex = query.length > 0 ? new RegExp(h.escapeRegexString(query), "gi") : null,
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
                                <th>System</th>
                                <th>Organ</th>
                                <th>Effect</th>
                                <th>Effect subtype</th>
                                <th>Name</th>
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
