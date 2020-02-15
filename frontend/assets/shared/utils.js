var deepCopy = function(d) {
        return JSON.parse(JSON.stringify(d));
    },
    docUrlRoot = "https://hawc.readthedocs.io/en/latest/",
    getAjaxHeaders = function(csrf) {
        return new Headers({
            "X-CSRFToken": csrf,
            "content-type": "application/json",
        });
    };

export {deepCopy};
export {docUrlRoot};
export {getAjaxHeaders};
