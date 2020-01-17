import _ from "lodash";
import React, {Component} from "react";
import PropTypes from "prop-types";
import ReactDOM from "react-dom";

import AggregateGraph from "riskofbias/robTable/components/AggregateGraph";
import RiskOfBiasDisplay from "riskofbias/robTable/components/RiskOfBiasDisplay";
import ShowAll from "riskofbias/robTable/components/ShowAll";

class StudyDisplay extends Component {
    constructor(props) {
        super(props);
        this.state = {
            scores: [],
        };
        this.selectActive = this.selectActive.bind(this);
        this.selectAllActive = this.selectActive.bind(this, {display: "all"});
    }

    isAllShown() {
        return this.state.scores.length == this.props.riskofbias.scores.length;
    }

    selectActive(selection) {
        if (selection.domain == "all") {
            let scores = this.isAllShown() ? [] : this.props.riskofbias.scores;
            this.setState({scores});
        } else {
            let domain = _.find(this.props.riskofbias.scores, {
                key: selection.domain,
            });
            if (selection.metric) {
                let metric = _.find(domain.values, {key: selection.metric});
                this.setState({
                    scores: [Object.assign({}, domain, {values: [metric]})],
                });
            } else {
                this.setState({scores: [domain]});
            }
        }
    }

    render() {
        return (
            <div>
                <AggregateGraph
                    domains={this.props.riskofbias.scores}
                    handleClick={this.selectActive}
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
    ReactDOM.render(<StudyDisplay riskofbias={data} config={data.config} />, element);
}
export default StudyDisplay;
