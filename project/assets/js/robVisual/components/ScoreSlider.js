import React, { Component } from 'react';

class ScoreSlider extends Component {

    handleChange(e){
        this.props.handleChange(e);
    }

    render(){
        let { threshold, max }= this.props;
        return (
            <div>
                <p className='help-block'>
                    Select the minimum quality threshold
                </p>
                <form name='scoreSliderForm'>
                    <input
                        type='range'
                        id='scoreSlider'
                        name='scoreSlider'
                        min='0' max={max}
                        defaultValue='0'
                        onChange={this.handleChange.bind(this)} />
                    <output>{threshold}</output>
                </form>
            </div>
        );
    }

}

export default ScoreSlider;
