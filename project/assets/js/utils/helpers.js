import React from 'react';
import _ from 'underscore';
import moment from 'moment';


var helpers = {
    noop: function(){
    },
    fetchGet: {
        credentials: 'same-origin',
    },
    fetchPost: function(csrf, obj, verb='POST'){
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
    fetchDelete: function(csrf){
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
};

export default helpers;
