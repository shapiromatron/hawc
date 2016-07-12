import React, { Component } from 'react';
import _ from 'underscore';
import { connect } from 'react-redux';

import Slider from 'robVisual/components/ScoreSlider';
import { fetchRobScores, setScoreThreshold } from 'robVisual/actions/Filter';


class ScoreSlider extends Component {

    constructor(props) {
        super(props);
        this.handleChange = this.handleChange.bind(this)
    }

    componentWillMount(){
        this.props.dispatch(fetchRobScores());
        this.setState({threshold: 0});
    }

    handleChange(e){
        let threshold = parseInt(e.target.value);
        this.setState({threshold});
        this.props.dispatch(setScoreThreshold(threshold));
    }

    render(){
        let threshold = this.state.threshold,
            max = _.max(this.props.scores, (item) => {
                return item.final_score;
            }).final_score;
        return (
            _.isEmpty(this.props.effects) ?
                null :
                <Slider
                    max={max} threshold={threshold}
                    handleChange={this.handleChange}/>
        );
    }
}

function mapStateToProps(state){
    return {
        effects: state.filter.selectedEffects,
        scores: state.filter.robScores,
    };
}

export default connect(mapStateToProps)(ScoreSlider);
