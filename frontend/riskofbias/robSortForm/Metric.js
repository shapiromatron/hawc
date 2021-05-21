import React, {Component} from "react";
import PropTypes from "prop-types";
import {observer, inject} from "mobx-react";

@inject("store")
@observer
class Metric extends Component {
    render() {
        const {domainIndex, metricIndex, metric} = this.props,
            {moveMetric} = this.props.store;

        return (
            <tr>
                <td>
                    {metric.name}
                    <br />
                    <br />
                    <strong>Required for animal bioassay: </strong>
                    {metric.required_animal ? (
                        <i className="fa fa-check"></i>
                    ) : (
                        <i className="fa fa-minus"></i>
                    )}
                    <br />
                    <strong>Required for epidemiological: </strong>
                    {metric.required_epi ? (
                        <i className="fa fa-check"></i>
                    ) : (
                        <i className="fa fa-minus"></i>
                    )}
                    <br />
                    <strong>Required for in-vitro: </strong>
                    {metric.required_invitro ? (
                        <i className="fa fa-check"></i>
                    ) : (
                        <i className="fa fa-minus"></i>
                    )}
                </td>
                <td>
                    <span dangerouslySetInnerHTML={{__html: metric.description}}></span>
                    <br />
                </td>
                <td>
                    <div className="btn-group">
                        <button
                            className="btn btn-info"
                            onClick={() => {
                                moveMetric(domainIndex, metricIndex, false);
                            }}>
                            <i className="fa fa-arrow-up"></i>
                        </button>
                        <button
                            className="btn btn-info"
                            onClick={() => {
                                moveMetric(domainIndex, metricIndex, true);
                            }}>
                            <i className="fa fa-arrow-down"></i>
                        </button>
                    </div>
                </td>
            </tr>
        );
    }
}

Metric.propTypes = {
    store: PropTypes.object,
    domainIndex: PropTypes.number.isRequired,
    metricIndex: PropTypes.number.isRequired,
    metric: PropTypes.object.isRequired,
};

export default Metric;
