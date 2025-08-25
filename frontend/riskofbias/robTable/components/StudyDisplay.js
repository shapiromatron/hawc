import _ from "lodash";
import PropTypes from "prop-types";
import React, {Component} from "react";
import {createRoot} from "react-dom/client";

import AggregateGraph from "./AggregateGraph";
import RiskOfBiasDisplay from "./RiskOfBiasDisplay";
import ShowAll from "./ShowAll";

class StudyDisplay extends Component {
    constructor(props) {
        super(props);
        this.state = {
            scores: [],
        };
        this.selectActive = this.selectActive.bind(this);
        this.selectAllActive = this.selectActive.bind(this, "all");
    }

    isAllShown() {
        return this.state.scores.length == this.props.riskofbias.scores.length;
    }

    selectActive(domain, metric) {
        if (domain == "all") {
            let scores = this.isAllShown() ? [] : this.props.riskofbias.scores;
            this.setState({scores});
        } else {
            let domain_scores = _.find(this.props.riskofbias.scores, {
                key: domain,
            });
            if (metric) {
                let metric_scores = _.find(domain_scores.values, {key: metric});
                this.setState({
                    scores: [Object.assign({}, domain, {values: [metric_scores]})],
                });
            } else {
                this.setState({scores: [domain_scores]});
            }
        }
    }

    render() {
        return (
            <div>
                <AggregateGraph
                    domains={this.props.riskofbias.scores}
                    handleSelectDomain={this.selectActive}
                    handleSelectMetric={this.selectActive}
                />
                <RiskOfBiasDisplay active={this.state.scores} config={this.props.config} />
                <ShowAll allShown={this.isAllShown()} handleClick={this.selectAllActive} />
            </div>
        );
    }
}

StudyDisplay.propTypes = {
    config: PropTypes.shape({
        display: PropTypes.string.isRequired,
        isForm: PropTypes.bool.isRequired,
    }).isRequired,
    riskofbias: PropTypes.shape({
        scores: PropTypes.arrayOf(
            PropTypes.shape({
                key: PropTypes.string.isRequired,
                values: PropTypes.arrayOf(
                    PropTypes.shape({
                        key: PropTypes.string.isRequired,
                        values: PropTypes.arrayOf(
                            PropTypes.shape({
                                score_symbol: PropTypes.string.isRequired,
                                score_shade: PropTypes.string.isRequired,
                                domain_name: PropTypes.string.isRequired,
                                metric: PropTypes.shape({
                                    name: PropTypes.string.isRequired,
                                    description: PropTypes.string.isRequired,
                                }).isRequired,
                                notes: PropTypes.string.isRequired,
                                score_description: PropTypes.string.isRequired,
                            }).isRequired
                        ).isRequired,
                    }).isRequired
                ).isRequired,
            }).isRequired
        ).isRequired,
    }).isRequired,
};

export function renderStudyDisplay(data, element) {
    const root = createRoot(element);
    root.render(<StudyDisplay riskofbias={data} config={data.config} />);
}
export default StudyDisplay;
