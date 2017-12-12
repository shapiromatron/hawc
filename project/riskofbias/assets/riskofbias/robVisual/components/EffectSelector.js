import React, { Component } from 'react';
import PropTypes from 'prop-types';
import _ from 'lodash';

import './EffectSelector.css';


class EffectSelector extends Component {

    constructor(props) {
        super(props);
        this.handleChange = this.handleChange.bind(this);
    }

    handleChange(e){
        this.props.handleChange(e);
    }

    render(){
        let { effects } = this.props;
        return (
            <div className='robEffectSelect'>
                <label className="control-label">
                    Effects to include
                </label>
                <select multiple='true'
                        size='8'
                        onChange={this.handleChange}>
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

EffectSelector.propTypes = {
    handleChange: PropTypes.func.isRequired,
    effects: PropTypes.arrayOf(
        PropTypes.string.isRequired
    ).isRequired,
};

export default EffectSelector;
