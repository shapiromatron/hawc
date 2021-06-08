import React, {Component} from "react";
import PropTypes from "prop-types";
import {observer, inject} from "mobx-react";

import ActionsBtn from "shared/components/ActionsBtn";
import h from "shared/utils/helpers";

const domainCreateUrl = id => `/rob/assessment/${id}/domain/create/`,
    domainUpdateUrl = id => `/rob/domain/${id}/update/`,
    domainDeleteUrl = id => `/rob/domain/${id}/delete/`,
    metricCreateUrl = id => `/rob/domain/${id}/metric/create/`,
    metricUpdateUrl = id => `/rob/metric/${id}/update/`,
    metricDeleteUrl = id => `/rob/metric/${id}/delete/`;

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
        const {store, domainIndex, domain} = this.props,
            {detailedView} = this.state,
            {moveDomain} = store,
            btnCaption = detailedView ? "Hide details" : "Show details";

        return (
            <>
                <ActionsBtn
                    extraClasses="mb-2"
                    items={[
                        <a key={0} className="dropdown-item" href={metricCreateUrl(domain.id)}>
                            <i className="fa fa-fw fa-plus"></i> Create new metric
                        </a>,
                        <button
                            type="button"
                            key={1}
                            className="dropdown-item"
                            onClick={() => this.setState({detailedView: !detailedView})}>
                            <i className="fa fa-fw fa-eye"></i>&nbsp;{btnCaption}
                        </button>,
                    ]}
                />
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
                            <th>
                                {detailedView ? (
                                    <ul className="mb-0">
                                        <li>Name: {domain.name}</li>
                                        <li>
                                            Overall confidence:&nbsp;
                                            {h.booleanCheckbox(domain.is_overall_confidence)}
                                        </li>
                                        <li>Description: {domain.description}</li>
                                    </ul>
                                ) : (
                                    domain.name
                                )}
                            </th>
                            <th>
                                <button
                                    className="btn btn-info"
                                    onClick={() => moveDomain(domainIndex, false)}>
                                    <i className="fa fa-arrow-up"></i>
                                </button>
                                &nbsp;
                                <button
                                    className="btn btn-info"
                                    onClick={() => moveDomain(domainIndex, true)}>
                                    <i className="fa fa-arrow-down"></i>
                                </button>
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
};

@observer
class MetricRow extends Component {
    render() {
        const {domainIndex, metricIndex, metric, moveMetric, detailedView} = this.props;
        return (
            <tr>
                <td>&ensp;Metric #{metricIndex + 1}</td>
                <td>
                    {detailedView ? (
                        <div className="container">
                            <div className="row">
                                <div className="col-md-4">
                                    <ul>
                                        <li>
                                            <b>Name:&nbsp;</b>
                                            {metric.name}
                                        </li>
                                        <li>
                                            <b>Short name:&nbsp;</b>
                                            {metric.short_name}
                                        </li>
                                        <li>
                                            <b>Required animal:&nbsp;</b>
                                            {h.booleanCheckbox(metric.required_animal)}
                                        </li>
                                        <li>
                                            <b>Required epi:&nbsp;</b>
                                            {h.booleanCheckbox(metric.required_epi)}
                                        </li>
                                        <li>
                                            <b>Required invitro:&nbsp;</b>
                                            {h.booleanCheckbox(metric.required_invitro)}
                                        </li>
                                        <li>
                                            <b>Hide description:&nbsp;</b>
                                            {h.booleanCheckbox(metric.hide_description)}
                                        </li>
                                        <li>
                                            <b>Use short name:&nbsp;</b>
                                            {h.booleanCheckbox(metric.use_short_name)}
                                        </li>
                                    </ul>
                                </div>
                                <div className="col-md-8">
                                    <p>
                                        <b>Description:&nbsp;</b>
                                    </p>
                                    <div
                                        dangerouslySetInnerHTML={{
                                            __html: metric.description,
                                        }}></div>
                                </div>
                            </div>
                        </div>
                    ) : (
                        metric.name
                    )}
                </td>
                <td>
                    <button
                        className="btn btn-info"
                        onClick={() => moveMetric(domainIndex, metricIndex, false)}>
                        <i className="fa fa-arrow-up"></i>
                    </button>
                    &nbsp;
                    <button
                        className="btn btn-info"
                        onClick={() => moveMetric(domainIndex, metricIndex, true)}>
                        <i className="fa fa-arrow-down"></i>
                    </button>
                </td>
                <td>
                    <a className="btn btn-info" href={metricUpdateUrl(metric.id)}>
                        <i className="fa fa-fw fa-edit"></i>&nbsp;Edit
                    </a>
                    &nbsp;
                    <a className="btn btn-danger" href={metricDeleteUrl(metric.id)}>
                        <i className="fa fa-fw fa-trash"></i>&nbsp;Delete
                    </a>
                </td>
            </tr>
        );
    }
}

MetricRow.propTypes = {
    domainIndex: PropTypes.number.isRequired,
    metricIndex: PropTypes.number.isRequired,
    metric: PropTypes.object.isRequired,
    moveMetric: PropTypes.func.isRequired,
    detailedView: PropTypes.bool.isRequired,
};

@inject("store")
@observer
class SortTable extends Component {
    render() {
        const {store} = this.props;
        return (
            <div>
                {store.domains.map((domain, domainIndex) => (
                    <DomainTable
                        key={`domain${domain.id}`}
                        domain={domain}
                        domainIndex={domainIndex}
                    />
                ))}
                <a
                    className="btn btn-primary float-right mb-3"
                    href={domainCreateUrl(store.config.assessment_id)}>
                    <i className="fa fa-fw fa-plus"></i> Create new domain
                </a>
            </div>
        );
    }
}

SortTable.propTypes = {
    store: PropTypes.object,
};

export default SortTable;
