import _ from "lodash";

import $ from "$";

const experimentFormStartup = function(form) {
    $(form)
        .find("#id_name")
        .focus();
};

const animalGroupFormStartup = function(form) {
    let printf = window.app.HAWCUtils.printf;

    let onSpeciesChange = function(e, onStrainUpdateComplete) {
        // only show proper strains for a given species
        let selected = $("#id_strain option:selected").val();
        let update_strain_opts = function(d) {
            var opts = _.map(d, function(v, i) {
                return printf('<option value="{0}">{1}</option>', v.id, v.name);
            }).join("");

            $("#id_strain").html(opts);
            $(printf('#id_strain option[value="{0}"]', selected)).prop("selected", true);

            if (onStrainUpdateComplete !== undefined) {
                onStrainUpdateComplete();
            }
        };
        $.get("/assessment/api/strain", {species: $("#id_species").val()}, update_strain_opts);
    };
    $(form)
        .find("#id_species")
        .change(onSpeciesChange)
        .trigger("change");

    // refresh species after "Add new strain" popup closes. Wait half a second
    // to give the addition, if any, time to register.
    $("a[title='Create strain']").on(window.app.HAWCUtils.HAWC_NEW_WINDOW_POPUP_CLOSING, function(
        e
    ) {
        setTimeout(function() {
            let numStrainsBefore = $("#id_strain option").length;

            // reload the species
            onSpeciesChange(null, function() {
                let strains = $("#id_strain option");

                if (strains.length > numStrainsBefore) {
                    // a new one was added; let's select it.
                    let highestId = -1;
                    strains.each(function() {
                        highestId = Math.max(Number($(this).val()), highestId);
                    });

                    $("#id_strain").val(highestId);
                }
            });
        }, 500);
    });
};

export default document => {
    document.body.addEventListener("htmx:load", e => {
        if (e.target.querySelector(".form-experiment")) {
            experimentFormStartup(e.target);
        } else if (e.target.querySelector(".form-animalgroup")) {
            animalGroupFormStartup(e.target);
        }
    });
};
