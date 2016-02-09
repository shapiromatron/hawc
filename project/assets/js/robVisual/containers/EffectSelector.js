import React, { Component } from 'react';
import _ from 'underscore';
import { connect } from 'react-redux';
import { fetchEffects } from 'robVisual/actions/Filter';


class EffectSelector extends Component {
    componentWillMount(){
        this.props.dispatch(fetchEffects());
    }

    handleSelect(){

    }

    render(){
        let effects = this.props.effects;
        return (
            <div>
                <select multiple="true">
                    {_.map(effects, (effect) => {
                        return <option key={effect} value={effect}>{effect}</option>;
                    })}
                </select>
                <p className='help-block'>
                    After effects have loaded, render options here.
                </p>
            </div>
        );
    }
}

function mapStateToProps(state) {
    return {
        effects: state.filters.effects,
    };
}

export default connect(mapStateToProps)(EffectSelector)
