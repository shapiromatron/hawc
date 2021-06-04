import React, {Component} from "react";
import PropTypes from "prop-types";
import {observer, inject} from "mobx-react";

@inject("store")
@observer
class DomainRow extends Component {
    render() {
        const {store, domainIndex, domain} = this.props,
            {moveDomain} = store;

        return (
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
                    </button>{" "}
                    <button
                        className="btn btn-info"
                        onClick={() => {
                            moveDomain(domainIndex, true);
                        }}>
                        <i className="fa fa-arrow-down"></i>
                    </button>
                </th>
                <th>
                    <a className="btn btn-info" href={`/rob/domain/${domain.id}/update/`}>
                        Edit
                    </a>{" "}
                    <a className="btn btn-danger" href={`/rob/domain/${domain.id}/delete/`}>
                        Delete
                    </a>
                </th>
            </tr>
        );
    }
}

DomainRow.propTypes = {
    store: PropTypes.object,
    domainIndex: PropTypes.number,
    domain: PropTypes.object,
};

@inject("store")
@observer
class MetricRow extends Component {
    render() {
        const {store, domainIndex, metricIndex, metric} = this.props,
            {moveMetric} = store;

        return (
            <tr>
                <td></td>
                <td>{metricIndex + 1}</td>
                <td>{metric.name}</td>
                <td>
                    <button
                        className="btn btn-info"
                        onClick={() => {
                            moveMetric(domainIndex, metricIndex, false);
                        }}>
                        <i className="fa fa-arrow-up"></i>
                    </button>{" "}
                    <button
                        className="btn btn-info"
                        onClick={() => {
                            moveMetric(domainIndex, metricIndex, true);
                        }}>
                        <i className="fa fa-arrow-down"></i>
                    </button>
                </td>
                <td>
                    <a className="btn btn-info" href={`/rob/metric/${metric.id}/update/`}>
                        Edit
                    </a>{" "}
                    <a className="btn btn-danger" href={`/rob/metric/${metric.id}/delete/`}>
                        Delete
                    </a>
                </td>
            </tr>
        );
    }
}

MetricRow.propTypes = {
    store: PropTypes.object,
    domainIndex: PropTypes.number,
    metricIndex: PropTypes.number,
    metric: PropTypes.object,
};

@observer
class AddMetricRow extends Component {
    render() {
        const {domain} = this.props;

        return (
            <tr>
                <td></td>
                <td></td>
                <td>
                    <a className="btn btn-primary" href={`/rob/domain/${domain.id}/metric/create/`}>
                        <i className="fa fa-fw fa-plus"></i> Add metric
                    </a>
                </td>
                <td></td>
                <td></td>
            </tr>
        );
    }
}

AddMetricRow.propTypes = {
    domain: PropTypes.object,
};

@inject("store")
@observer
class SortTable extends Component {
    render() {
        const {store} = this.props;

        return (
            <table className="table table-hover">
                <tbody>
                    {store.domains.map((domain, domainIndex) => {
                        return (
                            <>
                                <DomainRow
                                    key={`domain${domainIndex}`}
                                    domain={domain}
                                    domainIndex={domainIndex}
                                />
                                {domain.metrics.map((metric, metricIndex) => {
                                    return (
                                        <MetricRow
                                            key={`domain${domainIndex}_metric${metricIndex}`}
                                            domainIndex={domainIndex}
                                            metricIndex={metricIndex}
                                            metric={metric}
                                        />
                                    );
                                })}
                                <AddMetricRow domain={domain} />
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
