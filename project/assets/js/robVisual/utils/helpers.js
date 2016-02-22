import React from 'react';
import _ from 'underscore';
import moment from 'moment';

var helpers = {
    noop(){
    },
    fetchGet: {
        credentials: 'same-origin',
    },
    fetchPost(csrf, obj, verb='POST'){
        obj['csrfmiddlewaretoken'] = csrf;
        return {
            credentials: 'same-origin',
            method: verb,
            headers: new Headers({
                'X-CSRFToken': csrf,
                'content-type': 'application/json',
            }),
            body: JSON.stringify(obj),
        };
    },
    fetchDelete(csrf){
        return {
            credentials: 'same-origin',
            method: 'DELETE',
            headers: new Headers({
                'X-CSRFToken': csrf,
                'content-type': 'application/json',
            }),
            body: JSON.stringify({csrfmiddlewaretoken:  csrf}),
        };
    },
    getValue(target){
        switch(target.type){
        case 'checkbox':
            return target.checked;
        case 'number':
            return parseFloat(target.value);
        case 'select-one':  // use isFinite in-case value is 0
            let val = parseInt(target.value);
            return (_.isFinite(val)) ? val : target.value;
        case 'text':
        case 'textarea':
        default:
            return target.value;
        }
    },
    getPatch(originalObj, newObj){
        let patch = {};
        _.each(newObj, function(v, k){
            if (originalObj[k] !== v){
                if (v instanceof Array || v instanceof Object){
                    if (JSON.stringify(originalObj[k]) != JSON.stringify(v)){
                        patch[k] = v;
                    }
                } else {
                    patch[k] = v;
                }
            }
        });
        return patch;
    },
    getObjectURL(base, id){
        return `${base}${id}/`;
    },
    booleanCheckbox(val){
        if (val){
            return <i className='fa fa-check-square-o' title="checked"></i>;
        } else {
            return <i className='fa fa-square-o' title="un-checked"></i>;
        }
    },
    datetimeFormat(dt){
        return moment(dt).format('MMMM Do YYYY, h:mm:ss a');
    },
    goBack(e){
        if (e && e.preventDefault) e.preventDefault();
        window.history.back();
    },
    getInputDivClass(name, errors, extra=[]){
        extra.push('form-group');
        if (errors && errors[name]) extra.push('has-error');
        return extra.join(' ');
    },
    getTestUrl(apiUrl, route){
        return `${apiUrl}${route}`;
    },
    getEndpointsUrl(config, study_id=[], effect=[]){
        let effects = _.map(effect, (e) => { return `&effect[]=${e}`; }).join('').replace(' ', '+'),
            study_ids = _.map(study_id, (id) => { return `&study_id[]=${id}`; }).join('');
        return `${config.apiUrl}${config.endpoint_filter_url}${study_ids}${effects}`;
    },
    errorDict: {
        endpoints: 'Filtering results contain more than 100 endpoints. Increase the quality threshold or include fewer effects.',
        effects: 'At least one effect must be chosen.',
        empty: 'No endpoints were returned. Decrease the quality threshold or include more effects.'
    },
    formatErrors(error){
        error  = error.substr(-9);
        return helpers.errorDict[error];
    },
    deepCopy(object){
        return JSON.parse(JSON.stringify(object));
    },
};

export default helpers;
