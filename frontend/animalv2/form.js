import _ from "lodash";

import $ from "$";

// general approach lifted from https://stackoverflow.com/questions/501719/dynamically-adding-a-form-to-a-django-formset
const cloneSubformRow = function(lastRow, totalFormField) {
    var newElement = lastRow.clone(true);
    var total = totalFormField.val();
    newElement.find(":input").each(function() {
        var name = $(this)
            .attr("name")
            .replace("-" + (total - 1) + "-", "-" + total + "-");
        var id = "id_" + name;
        $(this)
            .attr({name, id})
            .val("")
            .removeAttr("checked");
    });
    newElement.find("label").each(function() {
        var newFor = $(this)
            .attr("for")
            .replace("-" + (total - 1) + "-", "-" + total + "-");
        $(this).attr("for", newFor);
    });
    total++;
    totalFormField.val(total);
    lastRow.after(newElement);

    // some of the DOM elements (the outer td and some of the help labeling)
    // are wrong; correct them
    newElement.find("td, small").each(function() {
        let loopEl = $(this);
        let incorrectId = loopEl.attr("id");
        loopEl.attr("id", incorrectId.replace("-" + (total - 2) + "-", "-" + (total - 1) + "-"));
    });
};

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

const dataExtractionFormStartup = function(form) {
    let onQualitativeChange = function() {
        let isQualOnly = $(form)
            .find("#id_is_qualitative_only")
            .is(":checked");

        let quantitativeFields = [
            "data_location",
            "dataset_type",
            "variance_type",
            "statistical_method",
            "statistical_power",
            "method_to_control_for_litter_effects",
            "values_estimated",
            "response_units",
            "dose_response_observations",
            "result_details",
        ];

        quantitativeFields.forEach(function(fieldName) {
            let parentDiv = $("#id_" + fieldName).parents("div.form-group");
            if (isQualOnly) {
                parentDiv.addClass("hidden");
            } else {
                parentDiv.removeClass("hidden");
            }
        });

        // note at this point we are NOT wiping any values; in form.is_valid
        // we will do another check for is_qualitative_only and set appropriate
        // values at that point if needed.
    };

    $(form)
        .find("#id_is_qualitative_only")
        .change(onQualitativeChange);
    onQualitativeChange();
};

const formsetSetup = function(form, prefixOrPrefixes) {
    if (!Array.isArray(prefixOrPrefixes)) {
        prefixOrPrefixes = [prefixOrPrefixes];
    }

    $(form)
        .find("button.add-subobject")
        .each(function(index, element) {
            $(this).click(function() {
                let formPrefix = prefixOrPrefixes[index];
                let parentWrapper = $(this).parent("div.formset_wrapper");
                let lastRow = parentWrapper.find("tr:last");
                let totalFormField = parentWrapper.find(
                    "input[name='" + formPrefix + "-TOTAL_FORMS']"
                );
                cloneSubformRow(lastRow, totalFormField);
            });
        });
};

export default document => {
    document.body.addEventListener("htmx:load", e => {
        if (e.target.querySelector(".form-experiment")) {
            experimentFormStartup(e.target);
        } else if (e.target.querySelector(".form-animalgroup")) {
            animalGroupFormStartup(e.target);
        } else if (e.target.querySelector(".form-treatment")) {
            formsetSetup(e.target, "dosegroupform");
        } else if (e.target.querySelector(".form-dataextraction")) {
            dataExtractionFormStartup(e.target);
            formsetSetup(e.target, ["groupleveldataform", "animalleveldataform"]);
        }
    });
};
