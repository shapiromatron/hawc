import _ from "lodash";

import $ from "$";

import {EXPOSURE_BIOMONITORING} from "./constants";

const designFormStartup = function (form) {
        $(form).find("#id_summary").focus();
    },
    exposureFormStartup = function (form) {
        // handle `exposure.measurement_type` change
        $(form)
            .find("select[name='measurement_type_0']")
            .change(evt => {
                // toggle visibility of related fields given change in field
                const el = evt.target,
                    row = el.closest("form").querySelector("#row_id_biomonitoring_matrix_2"),
                    values = $(el).val();

                _.includes(values, EXPOSURE_BIOMONITORING)
                    ? row.classList.remove("hidden")
                    : row.classList.add("hidden");
            })
            .trigger("change");
    };

export default document => {
    document.body.addEventListener("htmx:load", e => {
        if (e.target.querySelector(".form-design")) {
            designFormStartup(e.target);
        } else if (e.target.querySelector(".form-exposure")) {
            exposureFormStartup(e.target);
        }
    });
};
