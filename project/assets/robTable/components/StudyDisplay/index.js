import React, { Component, PropTypes } from 'react';
import ReactDOM from 'react-dom';

import AggregateGraph from 'robTable/components/AggregateGraph';
import RiskOfBiasDisplay from 'robTable/components/RiskOfBiasDisplay';
import ShowAll from 'robTable/components/ShowAll';


class StudyDisplay extends Component {

    constructor(props) {
        super(props);
        this.state = {
            scores: [],
        };
    }

    selectActive(selection){
        if(selection.domain == 'all'){
            this.setState({scores: this.props.riskofbias.scores});
        } else {
            let domain = _.findWhere(this.props.riskofbias.scores, {key: selection.domain});
            if(selection.metric){
                let metric = _.findWhere(domain.values, {key: selection.metric});
                this.setState({ scores: [Object.assign({}, domain, {values: [metric]})]});
            } else {
                this.setState({scores: [domain]});
            }
        }
    }

    render() {
        return (<div>
            <AggregateGraph domains={this.props.riskofbias.scores} handleClick={this.selectActive.bind(this)}/>
            <RiskOfBiasDisplay active={this.state.scores} config={this.props.config} />
            <ShowAll handleClick={this.selectActive.bind(this, {domain: 'all'})}/>
        </div>);
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
                values: PropTypes.arrayOf(PropTypes.shape({
                    key: PropTypes.string.isRequired,
                    values: PropTypes.arrayOf(PropTypes.shape({
                        score_symbol: PropTypes.string.isRequired,
                        score_shade: PropTypes.string.isRequired,
                        domain_name: PropTypes.string.isRequired,
                        metric: PropTypes.shape({
                            metric: PropTypes.string.isRequired,
                            description: PropTypes.string.isRequired,
                        }).isRequired,
                        notes: PropTypes.string.isRequired,
                        score_description: PropTypes.string.isRequired,
                    }).isRequired).isRequired,
                }).isRequired).isRequired,
            }).isRequired
        ).isRequired,
    }).isRequired,

};

export function renderStudyDisplay(data, element){
    ReactDOM.render(<StudyDisplay riskofbias={data} config={data.config} />, element);
}
export default StudyDisplay;
