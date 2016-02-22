import React, { Component, PropTypes } from 'react';


class ScoreSlider extends Component {

    handleChange(e){
        this.props.handleChange(e);
    }

    render(){
        let { threshold, max }= this.props;
        return (
            <div>
            <form name='scoreSliderForm'>
                <p className='help-block'>
                    Select the minimum confidence rating: <output><strong>{threshold}</strong></output>
                </p>
                <input
                    type='range'
                    id='scoreSlider'
                    name='scoreSlider'
                    min='0' max={max}
                    defaultValue='0'
                    onChange={this.handleChange.bind(this)} />
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
