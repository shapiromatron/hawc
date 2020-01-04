import { combineReducers } from 'redux';

import config from 'shared/reducers/Config';
import * as types from 'riskofbias/robTable/constants';

const defaultState = {
    isFetching: false,
    itemsLoaded: false,
    error: null,
    name: '',
    final: [],
    rob_response_values: [],
    riskofbiases: [],
    active: [],
};

function study(state = defaultState, action) {
    switch (action.type) {
        case types.REQUEST:
            return Object.assign({}, state, {
                isFetching: true,
            });

        case types.RECEIVE:
            return Object.assign({}, state, {
                name: action.study.short_citation,
                final: action.study.final,
                rob_response_values: action.study.rob_response_values,
                riskofbiases: action.study.riskofbiases,
                active: action.study.riskofbiases,
                isFetching: false,
                itemsLoaded: true,
            });

        case types.SET_ERROR:
            return Object.assign({}, state, {
                error: action.error,
            });

        case types.RESET_ERROR:
            return Object.assign({}, state, {
                error: null,
            });

        case types.UPDATE_FINAL_SCORES:
            return Object.assign({}, state, {
                final: action.score,
            });

        case types.SELECT_ACTIVE:
            if (_.isEmpty(action.domain) | (action.domain === 'none')) {
                return Object.assign({}, state, {
                    active: [],
                });
            }
            if (action.domain === 'all') {
                return Object.assign({}, state, {
                    active: state.riskofbiases,
                });
            }
            let domains = _.find(state.riskofbiases, { key: action.domain });
            if (action.metric) {
                let values = _.find(domains.values, { key: action.metric });
                return Object.assign({}, state, {
                    active: [Object.assign({}, domains, { values: [values] })],
                });
            }
            return Object.assign({}, state, {
                active: [domains],
            });

        default:
            return state;
    }
}

const rootReducer = combineReducers({
    config,
    study,
});

export default rootReducer;
