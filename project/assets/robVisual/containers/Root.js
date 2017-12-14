import React, { Component, PropTypes } from 'react';
import { Provider } from 'react-redux';

import EffectSelector from './EffectSelector';
import ScoreSlider from './ScoreSlider';
import ApplyFilters from './ApplyFilters';
import EndpointCardContainer from './EndpointCardContainer';
import { loadConfig } from 'shared/actions/Config';


class Root extends Component {

    componentWillMount(){
        this.props.store.dispatch(loadConfig());
    }

    render() {
        let store = this.props.store;
        return (
            <Provider store={store}>
                <div>
                    <h1>Endpoints by study Study Evaluation score</h1>
                    <p className='help-text'>
                        This <b>prototype</b> is an example of showing different
                        effects in the database filtered by Study Evaluation score.
                        A higher Study Evaluation score indicates a greater number
                        of low risk-of bias responses.
                    </p>
                    <EffectSelector />
                    <ScoreSlider />
                    <ApplyFilters />
                    <EndpointCardContainer />
                </div>
            </Provider>
        );
    }
}

Root.propTypes = {
    store: PropTypes.object.isRequired,
};

export default Root;
