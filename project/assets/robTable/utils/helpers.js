import _ from 'underscore';
import moment from 'moment';


const helpers = {
    noop(){
    },
    fetchGet: {
        credentials: 'same-origin',
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
    getObjectURL(host, base, id, assessment_id){
        return `${host}${base}${id}/?assessment_id=${assessment_id}/`;
    },
    datetimeFormat(dt){
        return moment(dt).format('MMMM Do YYYY, h:mm:ss a');
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
