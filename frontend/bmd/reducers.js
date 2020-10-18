import _ from "lodash";
import h from "shared/utils/helpers";

// import config from "shared/reducers/Config";
import * as types from "bmd/constants";

var tmp, tmp2, tmp3;

function bmd(state = defaultState, action) {
    switch (action.type) {
        case types.UPDATE_MODEL:
            tmp = h.deepCopy(state.modelSettings);
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
            tmp = h.deepCopy(state.bmrs);
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
