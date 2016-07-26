var deepCopy = function(d){
        return JSON.parse(JSON.stringify(d));
    },
    getAjaxHeaders = function(csrf){
        return new Headers({
            'X-CSRFToken': csrf,
            'content-type': 'application/json',
        });
    },
    toHawcString = function(v){
        // synced with method in hawc.js
        return (v > 0.001)?
            v.toLocaleString():
            v.toString();
    };


export {deepCopy};
export {getAjaxHeaders};
export {toHawcString};
