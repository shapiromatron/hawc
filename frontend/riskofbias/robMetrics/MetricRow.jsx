import {observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";

import DetailMetric from "../components/DetailMetric";

const metricUpdateUrl = id => `/rob/metric/${id}/update/`,
    metricDeleteUrl = id => `/rob/metric/${id}/delete/`;

@observer
class MetricRow extends Component {
    render() {
        const {domainIndex, metricIndex, metric, moveMetric, detailedView, metricCount} =
            this.props;
        return (
            <tr>
                <td>&ensp;Metric #{metricIndex + 1}</td>
                <td>{detailedView ? <DetailMetric object={metric} /> : metric.name}</td>
                <td>
                    {metricCount > 1 ? (
                        <button
                            className="btn btn-info"
                            onClick={() => moveMetric(domainIndex, metricIndex, false)}>
                            <i className="fa fa-arrow-up"></i>
                        </button>
                    ) : null}
                    &nbsp;
                    {metricCount > 1 ? (
                        <button
                            className="btn btn-info"
                            onClick={() => moveMetric(domainIndex, metricIndex, true)}>
                            <i className="fa fa-arrow-down"></i>
                        </button>
                    ) : null}
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
    metricCount: PropTypes.number.isRequired,
};

export default MetricRow;
