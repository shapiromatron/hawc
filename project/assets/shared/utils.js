var deepCopy = function(d){
        return JSON.parse(JSON.stringify(d));
    },
    getAjaxHeaders = function(csrf){
        return new Headers({
            'X-CSRFToken': csrf,
            'content-type': 'application/json',
        });
    };


export {deepCopy};
export {getAjaxHeaders};
