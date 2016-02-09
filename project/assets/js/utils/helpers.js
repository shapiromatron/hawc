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
    fetchBulk(csrf, obj, verb='PATCH'){
        obj['csrfmiddlewaretoken'] = csrf;
        return {
            credentials: 'same-origin',
            method: verb,
            headers: new Headers({
                'X-CSRFToken': csrf,
                'content-type': 'application/json',
                'X-CUSTOM-BULK-OPERATION': true,
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
            if (originalObj[k] !== v) patch[k] = v;
        });
        return patch;
    },
    getAssessmentApiUrl(config){
        return `${config.apiUrl}${config.assessment}?assessment_id=${config.assessment_id}`;
    },
    getEndpointApiURL(state, filterFields=false, fetchModel=false, ids=null){
        let getFields = fetchModel ? 'fields/' : '';
        let fields = (filterFields && state.endpoint.field) ? `&fields=${state.endpoint.field}` : '';
        let idList = ids ? `&ids=${ids}` : '';
        return `${state.config.apiUrl}${state.config[state.endpoint.type].url}${getFields}?assessment_id=${state.assessment.active.id}${fields}${idList}`;
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
    deepCopy(object){
        return JSON.parse(JSON.stringify(object));
    },
    caseToWords(string){
        return string
            // replace underscores and dashes with spaces
            .replace(/[_-]/g, ' ')
            // insert a space between lower followed by upper
            .replace(/([a-z])([A-Z])/g, '$1 $2')
            // insert a space between last upper in sequence followed by lower
            .replace(/\b([A-Z]+)([A-Z])([a-z])/, '$1 $2$3')
            // uppercase the first character of every word
            .replace(/\w\S*/g, function(txt) {
                return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
            });
    },
    extendBreadcrumbs(url){
        $('.breadcrumb').children().last().contents().eq(-2).wrap(`<a href=${url}></a>`);
    },
};

export default helpers;
