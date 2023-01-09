import {helpText} from "animal/EndpointForm/constants";
import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import Modal from "shared/components/Modal";
import h from "shared/utils/helpers";

const MAX_ROWS = 150;

@inject("store")
@observer
class Table extends Component {
    render() {
        const store = this.props.store,
            {filteredDataset, query, showModal, modalText} = this.props.store,
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
                                <th>
                                    System
                                    <button
                                        type="button"
                                        className="ml-1 btn btn-sm btn-info"
                                        onClick={() => {
                                            store.updateModal(true, helpText.system, "System");
                                        }}>
                                        <i className="fa fa-question"></i>
                                    </button>
                                </th>
                                <th>
                                    Organ
                                    <button
                                        type="button"
                                        className="ml-1 btn btn-sm btn-info"
                                        onClick={() => {
                                            store.updateModal(true, helpText.organ, "Organ");
                                        }}>
                                        <i className="fa fa-question"></i>
                                    </button>
                                </th>
                                <th>
                                    Effect
                                    <button
                                        type="button"
                                        className="ml-1 btn btn-sm btn-info"
                                        onClick={() => {
                                            store.updateModal(true, helpText.effect, "Effect");
                                        }}>
                                        <i className="fa fa-question"></i>
                                    </button>
                                </th>
                                <th>
                                    Effect subtype
                                    <button
                                        type="button"
                                        className="ml-1 btn btn-sm btn-info"
                                        onClick={() => {
                                            store.updateModal(
                                                true,
                                                helpText.effect_subtype,
                                                "Effect subtype"
                                            );
                                        }}>
                                        <i className="fa fa-question"></i>
                                    </button>
                                </th>
                                <th>
                                    Endpoint/Outcome
                                    <button
                                        type="button"
                                        className="ml-1 btn btn-sm btn-info"
                                        onClick={() => {
                                            store.updateModal(
                                                true,
                                                helpText.endpoint_name,
                                                "Endpoint/Outcome"
                                            );
                                        }}>
                                        <i className="fa fa-question"></i>
                                    </button>
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
                <Modal
                    isShown={showModal}
                    onClosed={() => {
                        store.updateModal(false, "");
                    }}>
                    <div className="modal-header">
                        <h4 className="mb-0">{store.modalHeader}</h4>
                        <button
                            type="button"
                            className="float-right close"
                            onClick={() => store.updateModal(false)}
                            aria-label="Close">
                            <span aria-hidden="true">&times;</span>
                        </button>
                    </div>
                    <div
                        className="modal-body container-fluid"
                        dangerouslySetInnerHTML={{__html: modalText}}></div>
                </Modal>
            </>
        );
    }
}
Table.propTypes = {
    store: PropTypes.object,
};

export default Table;
