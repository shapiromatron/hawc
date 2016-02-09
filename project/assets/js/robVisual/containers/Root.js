import React, { Component, PropTypes } from 'react';
import { Provider } from 'react-redux';

import EffectSelector from './EffectSelector';
import ScoreSlider from './ScoreSlider';
import ApplyFilters from './ApplyFilters';
import EndpointCardContainer from './EndpointCardContainer';
import { loadConfig } from 'robVisual/actions/config';

export default class Root extends Component {
    componentWillMount(){
        this.props.store.dispatch(loadConfig());
    }

    handleEffectSelect(){

    }

    handleScoreChange(){

    }

    handleSubmit(){

    }

    render() {
        return (
            <Provider store={this.props.store}>
                <div>
                    <h1>Risk of bias filtering</h1>
                    <EffectSelector handleSelect={this.handleEffectSelect.bind(this)} />
                    <ScoreSlider handleChange={this.handleScoreChange.bind(this)} />
                    <ApplyFilters handleSubmit={this.handleSubmit.bind(this)} />
                    <EndpointCardContainer/>
                </div>
            </Provider>
        );
    }
}

Root.propTypes = {
    store: PropTypes.object.isRequired,
};
