import React, {Component} from "react";
import PropTypes from "prop-types";
import {observer, inject} from "mobx-react";
import _ from "lodash";

import Metric from "./Metric";

@inject("store")
@observer
class Domain extends Component {
    render() {
        const {domainIndex, domain} = this.props,
            {moveDomain} = this.props.store;

        return (
            <>
                <h2 className="d-inline-block">{domain.name} Domain</h2>
                <div className="btn-group float-right">
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
                </div>
                <p
                    className="form-text text-muted"
                    dangerouslySetInnerHTML={{__html: domain.description}}></p>
                <table className="table table-compressed">
                    <colgroup>
                        <col width="40%"></col>
                        <col width="40%"></col>
                        <col width="20%"></col>
                    </colgroup>

                    <thead>
                        <tr>
                            <th>Metric</th>
                            <th>Description</th>
                            <th>Modify</th>
                        </tr>
                    </thead>
                    <tbody>
                        {domain.metrics.map((metric, metricIndex) => {
                            return (
                                <Metric
                                    key={metric.id}
                                    domainIndex={domainIndex}
                                    metricIndex={metricIndex}
                                    metric={metric}
                                />
                            );
                        })}
                    </tbody>
                </table>
            </>
        );
    }
}

Domain.propTypes = {
    store: PropTypes.object,
    domainIndex: PropTypes.number.isRequired,
    domain: PropTypes.object.isRequired,
};

export default Domain;
