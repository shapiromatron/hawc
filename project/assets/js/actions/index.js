import { CALL_API } from '../middleware/api';

export const ENDPOINT_TYPES_REQUEST = 'ENDPOINT_REQUEST';
export const ENDPOINT_TYPES_SUCCESS = 'ENDPOINT_SUCCESS';
export const ENDPOINT_TYPES_FAILURE = 'ENDPOINT_FAILURE';

function fetchEndpointTypes(assessment){
    return {
        [CALL_API]: {
            types: [ ENDPOINT_REQUEST, ENDPOINT_SUCCESS, ENDPOINT_FAILURE ],
            endpoint: `assessment/api/endpoints/?assessment_id=${assessment.id}`,
        },
    };
}

export function loadEndpointTypes(assessment_id, requiredFields = []){
    return (dispatch, getState) => {
        const endpointTypes = getState.entities.endpointTypes[assessment.id];
        if (endpointTypes && requiredFields.every((key) => endpointTypes.hasOwnProperty(key))){
            return null;
        }

        return dispatch(fetchEndpointTypes(assessment));
    };
}

// Resets the currently visible error message.
export function resetErrorMessage() {
    return {
        type: RESET_ERROR_MESSAGE,
    };
}
