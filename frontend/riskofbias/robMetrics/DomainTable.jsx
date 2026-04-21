import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import {ActionItem, ActionLink, ActionsButton} from "shared/components/ActionsButton";

import DetailDomain from "../components/DetailDomain";
import MetricRow from "./MetricRow";

const domainUpdateUrl = id => `/rob/domain/${id}/update/`,
    domainDeleteUrl = id => `/rob/domain/${id}/delete/`,
    metricCreateUrl = id => `/rob/domain/${id}/metric/create/`;

@inject("store")
@observer
class DomainTable extends Component {
    constructor(props) {
        super(props);
        this.state = {
            detailedView: false,
        };
    }

    render() {
        const {store, domainIndex, domain, domainCount} = this.props,
            {detailedView} = this.state,
            {moveDomain} = store,
            btnCaption = detailedView ? "Hide details" : "Show details";
        return (
            <>
                <div className="d-flex">
                    <ActionsButton
                        containerClasses="mb-2"
                        items={[
                            <ActionLink
                                key={0}
                                icon="fa-plus"
                                label="Create new metric"
                                href={metricCreateUrl(domain.id)}
                            />,
                            <ActionItem
                                key={1}
                                icon="fa-info-circle"
                                label={btnCaption}
                                onClick={() => this.setState({detailedView: !detailedView})}
                            />,
                        ]}
                    />
                </div>
                <table className="table mt-2">
                    <colgroup>
                        <col width="115px" />
                        <col />
                        <col width="120px" />
                        <col width="220px" />
                    </colgroup>
                    <thead>
                        <tr className="table-primary">
                            <th>Domain #{domainIndex + 1}</th>
                            <th>{detailedView ? <DetailDomain object={domain} /> : domain.name}</th>
                            <th>
                                {domainCount > 1 ? (
                                    <button
                                        className="btn btn-info"
                                        onClick={() => moveDomain(domainIndex, false)}>
                                        <i className="fa fa-arrow-up"></i>
                                    </button>
                                ) : null}
                                &nbsp;
                                {domainCount > 1 ? (
                                    <button
                                        className="btn btn-info"
                                        onClick={() => moveDomain(domainIndex, true)}>
                                        <i className="fa fa-arrow-down"></i>
                                    </button>
                                ) : null}
                            </th>
                            <th>
                                <a className="btn btn-info" href={domainUpdateUrl(domain.id)}>
                                    <i className="fa fa-fw fa-edit"></i>&nbsp;Edit
                                </a>
                                &nbsp;
                                <a className="btn btn-danger" href={domainDeleteUrl(domain.id)}>
                                    <i className="fa fa-fw fa-trash"></i>&nbsp;Delete
                                </a>
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        {domain.metrics.map((metric, metricIndex) => {
                            return (
                                <MetricRow
                                    key={`metric${metric.id}`}
                                    domainIndex={domainIndex}
                                    metricIndex={metricIndex}
                                    metric={metric}
                                    moveMetric={store.moveMetric}
                                    detailedView={detailedView}
                                    metricCount={domain.metrics.length}
                                />
                            );
                        })}
                    </tbody>
                </table>
            </>
        );
    }
}

DomainTable.propTypes = {
    store: PropTypes.object,
    domainIndex: PropTypes.number.isRequired,
    domain: PropTypes.object.isRequired,
    domainCount: PropTypes.number.isRequired,
};

export default DomainTable;
