import $ from "$";
import _ from "lodash";

import {EXPOSURE_BIOMONITORING} from "./constants";

const designFormStartup = function (form) {
        $(form).find("#id_summary").focus();
    },
    exposureFormStartup = function (form) {
        // handle `exposure.measurement_type` change
        $(form)
            .find('[data-name="measurement_type"]')
            .change(evt => {
                // toggle visibility of related fields given change in field
                const el = evt.target,
                    row = el
                        .closest("form")
                        .querySelector('[data-name="biomonitoring_matrix"]')
                        .closest(".form-row"),
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
