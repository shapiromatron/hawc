import React, { Component } from 'react';
import _ from 'underscore';
import { connect } from 'react-redux';
// import { fetchEffects } from 'robVisual/actions/Filters';

class ScoreSlider extends Component {

    handleChange(e){

    }

    render(){
        return (
            <div>
                <input type='range' min='0' max='100' onChange={this.handleChange.bind(this)}></input>
                <p className='help-block'>
                    After study-quality values have loaded, render options here.
                </p>
            </div>
        );
    }
}

function mapStateToProps(state){
    return {}
}

export default connect(mapStateToProps)(ScoreSlider);
