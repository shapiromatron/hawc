import React, { Component } from 'react';
import _ from 'underscore';
import { connect } from 'react-redux';

import Selector from 'robVisual/components/EffectSelector';
import { fetchEffects, selectEffects } from 'robVisual/actions/Filter';


class EffectSelector extends Component {
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
            <Selector effects={this.props.effects} handleChange={this.handleChange.bind(this)}/>
        );
    }
}

function mapStateToProps(state) {
    return {
        effects: state.filter.effects,
    };
}

export default connect(mapStateToProps)(EffectSelector);
