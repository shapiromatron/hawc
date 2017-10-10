import * as types from 'riskofbias/robScoreCleanup/constants';


export function setError(error){
    return {
        type: types.SET_ERROR,
        error,
    };
}

export function resetError(){
    return {
        type: types.RESET_ERROR,
    };
}