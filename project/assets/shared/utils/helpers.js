import $ from '$';
import React from 'react';
import _ from 'lodash';
import moment from 'moment';

const helpers = {
    noop() {},
    fetchGet: {
        credentials: 'same-origin',
    },
    fetchPost(csrf, obj, verb = 'POST') {
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
    fetchForm(csrf, form, verb = 'POST') {
        // form should be a <form> html element
        return {
            credentials: 'same-origin',
            method: verb,
            headers: new Headers({
                'X-CSRFToken': csrf,
                'content-type': 'application/x-www-form-urlencoded',
            }),
            body: $(form).serialize(),
        };
    },

    fetchBulk(csrf, obj, verb = 'PATCH') {
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
    fetchDelete(csrf) {
        return {
            credentials: 'same-origin',
            method: 'DELETE',
            headers: new Headers({
                'X-CSRFToken': csrf,
                'content-type': 'application/json',
            }),
            body: JSON.stringify({ csrfmiddlewaretoken: csrf }),
        };
    },
    goBack(e) {
        if (e && e.preventDefault) e.preventDefault();
        window.history.back();
    },
    getValue(target) {
        switch (target.type) {
            case 'checkbox':
                return target.checked;
            case 'number':
                return parseFloat(target.value);
            case 'select-one': // use isFinite in-case value is 0
                let val = parseInt(target.value);
                return _.isFinite(val) ? val : target.value;
            case 'text':
            case 'textarea':
            default:
                return target.value;
        }
    },
    getObjectUrl(host, base, id) {
        return `${host}${base}${id}/`;
    },
    getListUrl(host, base) {
        return `${host}${base}`;
    },
    getUrlWithAssessment(url, assessment_id) {
        return `${url}?assessment_id=${assessment_id}`;
    },
    getBulkUrl(host, base, ids = null) {
        return `${host}${base}&ids=${ids}`;
    },
    datetimeFormat(dt) {
        return moment(dt).format('MMMM Do YYYY, h:mm:ss a');
    },
    booleanCheckbox(val) {
        if (val) {
            return <i className="fa fa-check-square-o" title="checked" />;
        } else {
            return <i className="fa fa-square-o" title="un-checked" />;
        }
    },
    getInputDivClass(name, errors, extra = []) {
        extra.push('form-group');
        if (errors && errors[name]) extra.push('has-error');
        return extra.join(' ');
    },
    deepCopy(object) {
        return JSON.parse(JSON.stringify(object));
    },
    caseToWords(string) {
        return (
            string
                // replace underscores and dashes with spaces
                .replace(/[_-]/g, ' ')
                // insert a space between lower followed by upper
                .replace(/([a-z])([A-Z])/g, '$1 $2')
                // insert a space between last upper in sequence followed by lower
                .replace(/\b([A-Z]+)([A-Z])([a-z])/, '$1 $2$3')
                // uppercase the first character of first word
                .replace(/\w\S*/, function(txt) {
                    return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
                })
        );
    },
    hideRobScore(assessment_id) {
        // TODO - remove 100500031 hack
        return assessment_id === 100500031;
    },
};

export default helpers;
