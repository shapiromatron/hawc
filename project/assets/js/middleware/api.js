const API_ROOT = 'https://' + window.location.host

function callApi(endpoint){
    const fullUrl = (endpoint.indexOf(API_ROOT) === -1) ? API_ROOT + endpoint : endpoint

    return fetch(fullUrl)
        .then(response =>
        response.json().then(json => ({ json, response }))
    ).then(({ json, response }) => {
        if (!response.ok){
            return Promise.reject(json)
        }

        returnObject.assign({}, JSON.stringify(json))
    })
}

export const CALL_API = Symbol('Call API')

export default store => next => action => {
    const callAPI = action[CALL_API]
    if (typeof callAPI === 'undefined') {
        return next(action)
    }

    let { endpoint } = callAPI
    const { types } = callAPI

    if (typeof endpoint === 'function'){
        endpoint = endpoint(store.getState())
    }
    if (typeof endpoint !== 'string'){
        throw new Error('Specify a string endpoint URL.')
    }
    if (!Array.isArray(types) || types.length !== 3){
        throw new Error('Expected an array of three action types.')
    }
    if(!types.every(type => typeof type === 'string')){
        throw new Error('Expecte action types to be strings.')
    }

    function actionWith(data){
        const finalAction = Object.assign({}, action, data)
        delete finalAction[CALL_API]
        return finalAction
    }

    const [ requestType, successType, failureType ] = types
    next(actionWith({ type: requestType }))

    return callApi(endpoint).then(
        response => next(actionWith({
            response,
            type: successType
        })),
        error => next(actionWith({
            type: failureType,
            error: error.message || 'Something bad happened'
        }))
    )
}
