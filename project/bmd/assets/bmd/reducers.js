import _ from 'lodash';
import { deepCopy } from 'shared/utils';

import { combineReducers } from 'redux';

import config from 'shared/reducers/Config';
import * as types from 'bmd/constants';

import { apply_logic } from 'bmd/models/logic';

/*
    The user-interface is normalized more than the serialized data on the
    server. The `models` includes duplicate model-settings; `modelSettings`
    are derived from the models and the allModelOptions.
*/
const defaultState = {
    hasSession: false,
    hasEndpoint: false,
    hasExecuted: false,
    endpoint: null,
    dataType: null,
    doseUnits: null,
    models: [],
    modelSettings: [],
    selectedModelOptionIndex: null,
    selectedModelOption: null,
    bmrs: [],
    selectedBmrIndex: null,
    selectedBmr: null,
    allModelOptions: [],
    allBmrOptions: null,
    isExecuting: false,
    validationErrors: [],
    selectedOutputs: [],
    hoverModel: null,
    selectedModelId: null,
    selectedModelNotes: '',
    logic: [],
    logicApplied: false,
};

var tmp, tmp2, tmp3;

function bmd(state = defaultState, action) {
    switch (action.type) {
        case types.RECEIVE_ENDPOINT:
            return Object.assign({}, state, {
                endpoint: action.endpoint,
                dataType: action.endpoint.data.data_type,
                hasEndpoint: true,
                logicApplied: false,
            });

        case types.RECEIVE_SESSION:
            // add key-prop to each values dict for parameter
            _.each(action.settings.allModelOptions, (d) =>
                _.each(d.defaults, (v, k) => (v.key = k))
            );

            // create model-settings
            // 1) only get the first bmr instance of the model
            // 2) add defaults based on the model name
            tmp2 = _.keyBy(action.settings.allModelOptions, 'name');

            action.settings.models.forEach((d) => (d.defaults = tmp2[d.name].defaults));

            tmp = _.chain(action.settings.models)
                .filter((d) => d.bmr_id === 0)
                .map((d) => deepCopy(d))
                .value();

            tmp3 = action.settings.selected_model || {};

            return Object.assign({}, state, {
                models: action.settings.models,
                modelSettings: tmp,
                bmrs: action.settings.bmrs,
                doseUnits: action.settings.dose_units,
                allModelOptions: action.settings.allModelOptions,
                allBmrOptions: _.keyBy(action.settings.allBmrOptions, 'type'),
                selectedModelId: tmp3.model || null,
                selectedModelNotes: tmp3.notes || '',
                logic: action.settings.logic,
                hasSession: true,
                hasExecuted: action.settings.is_finished,
                logicApplied: false,
            });

        case types.APPLY_LOGIC:
            apply_logic(state.logic, state.models, state.endpoint, state.doseUnits);
            return Object.assign({}, state, {
                logicApplied: true,
            });

        case types.CHANGE_UNITS:
            return Object.assign({}, state, {
                doseUnits: action.doseUnits,
            });

        case types.CREATE_MODEL:
            tmp = Object.assign(deepCopy(state.allModelOptions[action.modelIndex]), {
                overrides: {},
            });
            return Object.assign({}, state, {
                modelSettings: [...state.modelSettings, tmp],
            });

        case types.SELECT_MODEL:
            return Object.assign({}, state, {
                selectedModelOptionIndex: action.modelIndex,
                selectedModelOption: state.modelSettings[action.modelIndex],
            });

        case types.UPDATE_MODEL:
            tmp = deepCopy(state.modelSettings);
            tmp[state.selectedModelOptionIndex].overrides = action.values;
            return Object.assign({}, state, {
                modelSettings: tmp,
                selectedModelOptionIndex: null,
                selectedModelOption: null,
            });

        case types.DELETE_MODEL:
            tmp = state.modelSettings
                .slice(0, state.selectedModelOptionIndex)
                .concat(state.modelSettings.slice(state.selectedModelOptionIndex + 1));
            return Object.assign({}, state, {
                modelSettings: tmp,
                selectedModelOptionIndex: null,
                selectedModelOption: null,
            });

        case types.TOGGLE_VARIANCE:
            tmp = _.map(state.modelSettings, (d) => {
                tmp2 = deepCopy(d);
                tmp2.overrides.constant_variance = tmp2.overrides.constant_variance === 0 ? 1 : 0;
                return tmp2;
            });
            return Object.assign({}, state, {
                modelSettings: tmp,
            });

        case types.ADD_ALL_MODELS:
            tmp = _.map(state.allModelOptions, (d) =>
                Object.assign(deepCopy(d), { overrides: {} })
            );
            return Object.assign({}, state, {
                modelSettings: [...state.modelSettings, ...tmp],
            });

        case types.REMOVE_ALL_MODELS:
            return Object.assign({}, state, {
                modelSettings: [],
            });

        case types.CREATE_BMR:
            return Object.assign({}, state, {
                bmrs: [...state.bmrs, _.values(state.allBmrOptions)[0]],
            });

        case types.SELECT_BMR:
            return Object.assign({}, state, {
                selectedBmrIndex: action.bmrIndex,
                selectedBmr: state.bmrs[action.bmrIndex],
            });

        case types.UPDATE_BMR:
            tmp = deepCopy(state.bmrs);
            tmp[state.selectedBmrIndex] = action.values;
            return Object.assign({}, state, {
                bmrs: tmp,
                selectedBmrIndex: null,
                selectedBmr: null,
            });

        case types.DELETE_BMR:
            tmp = state.bmrs
                .slice(0, state.selectedBmrIndex)
                .concat(state.bmrs.slice(state.selectedBmrIndex + 1));
            return Object.assign({}, state, {
                bmrs: tmp,
                selectedBmrIndex: null,
                selectedBmr: null,
            });

        case types.VALIDATE:
            return Object.assign({}, state, {
                validationErrors: action.validationErrors,
                isExecuting: false,
            });

        case types.EXECUTE_START:
            return Object.assign({}, state, {
                isExecuting: true,
            });

        case types.EXECUTE_STOP:
            return Object.assign({}, state, {
                isExecuting: false,
            });

        case types.SELECT_OUTPUT:
            return Object.assign({}, state, {
                selectedOutputs: action.models,
            });

        case types.HOVER_MODEL:
            return Object.assign({}, state, {
                hoverModel: action.model,
            });

        case types.SET_SELECTED_MODEL:
            return Object.assign({}, state, {
                selectedModelId: action.model_id,
                selectedModelNotes: action.notes,
            });

        default:
            return state;
    }
}

const rootReducer = combineReducers({
    config,
    bmd,
});

export default rootReducer;
