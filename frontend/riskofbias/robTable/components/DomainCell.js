import _ from "lodash";
import React, {Component} from "react";
import PropTypes from "prop-types";

import MetricCell from "./MetricCell";

import "./DomainCell.css";

class DomainCell extends Component {
    componentDidMount() {
        $(".tooltips").tooltip();
    }

    render() {
        // scoresByMetric is an array of score arrays, grouped by metric
        let {domain, handleSelectDomain, handleSelectMetric} = this.props,
            scoresByMetric = _.map(this.props.domain.values, "values"),
            domainName = scoresByMetric[0][0].domain_name;

        return (
            <div className="domain-cell" style={{flex: scoresByMetric.length}}>
                <div className="header-box" onClick={() => handleSelectDomain(domain.key)}>
                    <span className="domain-header">{domainName}</span>
                </div>
                <div className="score-row">
                    {scoresByMetric.map(scores => {
                        return (
                            <MetricCell
                                key={scores[0].metric_id}
                                scores={scores}
                                handleClick={handleSelectMetric}
                            />
                        );
                    })}
                </div>
            </div>
        );
    }
}

DomainCell.propTypes = {
    domain: PropTypes.shape({
        key: PropTypes.string.isRequired,
        values: PropTypes.arrayOf(
            PropTypes.shape({
                values: PropTypes.arrayOf(
                    PropTypes.shape({
                        id: PropTypes.number.isRequired,
                        score_symbol: PropTypes.string.isRequired,
                        score_shade: PropTypes.string.isRequired,
                        bias_direction: PropTypes.number.isRequired,
                        domain_name: PropTypes.string.isRequired,
                    })
                ).isRequired,
            })
        ).isRequired,
    }).isRequired,
    handleSelectDomain: PropTypes.func.isRequired,
    handleSelectMetric: PropTypes.func.isRequired,
};

export default DomainCell;
