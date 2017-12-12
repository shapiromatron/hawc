import React, { Component } from 'react';
import PropTypes from 'prop-types';


class ScoreSlider extends Component {

    constructor(props) {
        super(props);
        this.handleChange = this.handleChange.bind(this);
    }

    handleChange(e){
        this.props.handleChange(e);
    }

    render(){
        let { threshold, max }= this.props;
        return (
            <div>
            <form name='scoreSliderForm'>
                <label className="control-label">
                    Minimum risk of bias rating: <span>{threshold}</span>
                </label>
                <input
                    type='range'
                    id='scoreSlider'
                    name='scoreSlider'
                    min='0' max={max}
                    defaultValue='0'
                    onChange={this.handleChange} />
            </form>
            </div>
        );
    }

}

ScoreSlider.propTypes = {
    max: PropTypes.number.isRequired,
    threshold: PropTypes.number.isRequired,
    handleChange: PropTypes.func.isRequired,
};

export default ScoreSlider;
