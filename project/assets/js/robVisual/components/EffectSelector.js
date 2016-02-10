import React, { Component } from 'react';
import _ from 'underscore';

class EffectSelector extends Component {

    handleChange(e){
        this.props.handleChange(e);
    }

    render(){
        let { effects } = this.props;
        return (
            <div className='robEffectSelect'>
                <p className='help-block'>
                    Select effects to include
                </p>
                <select multiple='true' size='8' onChange={this.handleChange.bind(this)}>
                    {_.map(effects, (effect) => {
                        return (
                            <option key={effect} value={effect}>
                                {effect}
                            </option>
                        );
                    })}
                </select>
            </div>
        );
    }
}

export default EffectSelector;
