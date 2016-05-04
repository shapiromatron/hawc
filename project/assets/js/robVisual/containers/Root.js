import React, { Component, PropTypes } from 'react';
import { Provider } from 'react-redux';

import EffectSelector from './EffectSelector';
import ScoreSlider from './ScoreSlider';
import ApplyFilters from './ApplyFilters';
import EndpointCardContainer from './EndpointCardContainer';
import { loadConfig } from 'robVisual/actions/config';


class Root extends Component {

    componentWillMount(){
        this.props.store.dispatch(loadConfig());
    }

    render() {
        let store = this.props.store;
        return (
            <Provider store={store}>
                <div>
                    <h1>View endpoints by risk of bias</h1>
                    <EffectSelector />
                    <ScoreSlider />
                    <ApplyFilters />
                    <EndpointCardContainer/>
                </div>
            </Provider>
        );
    }
}

Root.propTypes = {
    store: PropTypes.object.isRequired,
};

export default Root;
