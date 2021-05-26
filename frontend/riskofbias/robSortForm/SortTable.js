import React, {Component} from "react";
import PropTypes from "prop-types";
import {observer, inject} from "mobx-react";

@inject("store")
@observer
class SortTable extends Component {
    render() {
        const {store} = this.props,
            {moveDomain, moveMetric} = store;

        return (
            <table className="table table-hover">
                <tbody>
                    {store.domains.map((domain, domainIndex) => {
                        return (
                            <>
                                <tr>
                                    <th>{domainIndex + 1}</th>
                                    <th colSpan="2">{domain.name}</th>
                                    <th>
                                        <button
                                            className="btn btn-info"
                                            onClick={() => {
                                                moveDomain(domainIndex, false);
                                            }}>
                                            <i className="fa fa-arrow-up"></i>
                                        </button>
                                        <button
                                            className="btn btn-info"
                                            onClick={() => {
                                                moveDomain(domainIndex, true);
                                            }}>
                                            <i className="fa fa-arrow-down"></i>
                                        </button>
                                    </th>
                                </tr>
                                {domain.metrics.map((metric, metricIndex) => {
                                    return (
                                        <>
                                            <tr>
                                                <td></td>
                                                <td>{metricIndex + 1}</td>
                                                <td>{metric.name}</td>
                                                <td>
                                                    <button
                                                        className="btn btn-info"
                                                        onClick={() => {
                                                            moveMetric(
                                                                domainIndex,
                                                                metricIndex,
                                                                false
                                                            );
                                                        }}>
                                                        <i className="fa fa-arrow-up"></i>
                                                    </button>
                                                    <button
                                                        className="btn btn-info"
                                                        onClick={() => {
                                                            moveMetric(
                                                                domainIndex,
                                                                metricIndex,
                                                                true
                                                            );
                                                        }}>
                                                        <i className="fa fa-arrow-down"></i>
                                                    </button>
                                                </td>
                                            </tr>
                                        </>
                                    );
                                })}
                            </>
                        );
                    })}
                </tbody>
            </table>
        );
    }
}

SortTable.propTypes = {
    store: PropTypes.object,
};

export default SortTable;
