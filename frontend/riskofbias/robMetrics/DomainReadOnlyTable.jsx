import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";

import DetailDomain from "../components/DetailDomain";
import DetailMetric from "../components/DetailMetric";

@inject("store")
@observer
class DomainReadOnlyTable extends Component {
    render() {
        const {domainIndex, domain} = this.props;

        return (
            <table className="table mt-2">
                <colgroup>
                    <col width="115px" />
                    <col />
                </colgroup>
                <thead>
                    <tr className="table-primary">
                        <th>Domain #{domainIndex + 1}</th>
                        <th>
                            <DetailDomain object={domain} />
                        </th>
                    </tr>
                </thead>
                <tbody>
                    {domain.metrics.map((metric, metricIndex) => {
                        return (
                            <tr key={`metric${metric.id}`}>
                                <td>Metric #{metricIndex + 1}</td>
                                <td>
                                    <DetailMetric object={metric} />
                                </td>
                            </tr>
                        );
                    })}
                </tbody>
            </table>
        );
    }
}

DomainReadOnlyTable.propTypes = {
    store: PropTypes.object,
    domainIndex: PropTypes.number.isRequired,
    domain: PropTypes.object.isRequired,
};

export default DomainReadOnlyTable;
