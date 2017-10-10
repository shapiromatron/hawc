import React, { Component } from 'react';
import _ from 'underscore';
import { connect } from 'react-redux';

import Selector from 'riskofbias/robVisual/components/EffectSelector';
import { fetchEffects, selectEffects } from 'riskofbias/robVisual/actions/Filter';


class EffectSelector extends Component {

    constructor(props) {
        super(props);
        this.handleChange = this.handleChange.bind(this);
    }

    componentWillMount(){
        this.props.dispatch(fetchEffects());
    }

    handleChange(e){
        let selectedOptions = _.map(e.target.selectedOptions, (option) => {
            return option.value;
        });
        this.props.dispatch(selectEffects(selectedOptions));
    }

    render(){
        return (
            <Selector
                effects={this.props.effects}
                handleChange={this.handleChange}/>
        );
    }
}

function mapStateToProps(state) {
    return {
        effects: state.filter.effects,
    };
}

export default connect(mapStateToProps)(EffectSelector);
