import * as types from '../constants/ActionTypes';
import _ from 'underscore';

let defaultState = {
    robScoreThreshold: null,
    selectedEffects: null,
    endpoints: [],
    isFetchingEndpoints: false,
    robScores: [],
    isFetchingRobScores: false,
    effects: [],
    isFetchingEffects: false,
};

export default function (state=defaultState, action){
    switch (action.type){

    default:
        return state;
    }
}
