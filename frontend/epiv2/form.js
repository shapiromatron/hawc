import $ from "$";

import {EXPOSURE_BIOMONITORING} from "./constants";

const exposureFormStartup = function(form) {
    // handle `exposure.measurement_type` change
    $(form)
        .find("select[name='measurement_type']")
        .change(evt => {
            // toggle visibility of related fields given change in field
            const el = evt.target,
                row = el.closest("form").querySelector("#row_id_biomonitoring_matrix_2");
            el.value === EXPOSURE_BIOMONITORING
                ? row.classList.remove("hidden")
                : row.classList.add("hidden");
        })
        .trigger("change");
};

export default document => {
    document.body.addEventListener("htmx:load", e => {
        if (e.target.querySelector(".form-design")) {
            $(e.target)
                .find(".html5text")
                .quillify();
            $(e.target)
                .find("#id_study_design")
                .focus();
        }

        if (e.target.querySelector(".form-exposure")) {
            exposureFormStartup(e.target);
        }
    });
};
