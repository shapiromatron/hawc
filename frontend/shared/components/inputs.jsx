import React from "react";

const errorsDiv = function (errors) {
        return errors && errors.length > 0 ? (
            <div className="invalid-feedback"> {errors.join("; ")}</div>
        ) : null;
    },
    inputClass = function (classes, errors) {
        return errors && errors.length > 0 ? `${classes} is-invalid` : classes;
    };

export {errorsDiv, inputClass};
