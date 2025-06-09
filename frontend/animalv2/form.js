import _ from "lodash";

import $ from "$";

const cloneSubformRow = function (lastRow, totalFormField) {
        // adapted from https://stackoverflow.com/questions/501719/
        const newElement = lastRow.clone(true);
        let total = totalFormField.val();
        newElement.find(":input").each(function () {
            const name = $(this)
                    .attr("name")
                    .replace(`-${total - 1}-`, `-${total}-`),
                id = `id_${name}`;
            $(this).attr({name, id}).val("").removeAttr("checked");
        });
        newElement.find("label").each(function () {
            var newFor = $(this)
                .attr("for")
                .replace(`-${total - 1}-`, `-${total}-`);
            $(this).attr("for", newFor);
        });
        total++;
        totalFormField.val(total);
        lastRow.after(newElement);

        // TODO - some DOM elements (the outer td and some of the help labeling) are wrong; fix
        newElement.find("td, small").each(function () {
            const loopEl = $(this),
                incorrectId = loopEl.attr("id");
            loopEl.attr("id", incorrectId.replace(`-${total - 2}-`, `-${total - 1}-`));
        });
    },
    experimentFormStartup = function (form) {
        $(form).find("#id_name").focus();
    },
    animalGroupFormStartup = function (form) {
        // TODO - fix - name is `animalgroup-1-species`
        let onSpeciesChange = function (_e, onStrainUpdateComplete) {
            // only show proper strains for a given species
            let selected = $("#id_strain option:selected").val();
            let update_strain_opts = function (d) {
                var opts = _.map(d, function (v, _i) {
                    return `<option value="${v.id}">${v.name}</option>`;
                }).join("");

                $("#id_strain").html(opts);
                $(`#id_strain option[value="${selected}"]`).prop("selected", true);

                if (onStrainUpdateComplete !== undefined) {
                    onStrainUpdateComplete();
                }
            };
            $.get("/assessment/api/strain", {species: $("#id_species").val()}, update_strain_opts);
        };
        $(form).find("#id_species").change(onSpeciesChange).trigger("change");

        // refresh species after "Add new strain" popup closes. Wait half a second
        // to give the addition, if any, time to register.
        $("a[title='Create strain']").on(
            window.app.HAWCUtils.HAWC_NEW_WINDOW_POPUP_CLOSING,
            function (_e) {
                setTimeout(function () {
                    let numStrainsBefore = $("#id_strain option").length;

                    // reload the species
                    onSpeciesChange(null, function () {
                        let strains = $("#id_strain option");

                        if (strains.length > numStrainsBefore) {
                            // a new one was added; let's select it.
                            let highestId = -1;
                            strains.each(function () {
                                highestId = Math.max(Number($(this).val()), highestId);
                            });

                            $("#id_strain").val(highestId);
                        }
                    });
                }, 500);
            }
        );
    },
    dataExtractionFormStartup = function (form) {
        // TODO fix - names are dataextraction-1-is_qualitative_only
        let onQualitativeChange = function () {
            let isQualOnly = $(form).find("#id_is_qualitative_only").is(":checked");

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

            quantitativeFields.forEach(function (fieldName) {
                // ok to just hide values; the server will validate
                let parentDiv = $(`#id_${fieldName}`).parents("div.form-group");
                if (isQualOnly) {
                    parentDiv.addClass("hidden");
                } else {
                    parentDiv.removeClass("hidden");
                }
            });
        };

        $(form).find("#id_is_qualitative_only").change(onQualitativeChange).trigger("change");
    },
    formsetSetup = function (form, prefixes) {
        if (!Array.isArray(prefixes)) {
            prefixes = [prefixes];
        }

        $(form)
            .find("button.add-subobject")
            .each(function (index, _element) {
                $(this).click(function () {
                    const formPrefix = prefixes[index],
                        parentWrapper = $(this).parent("div.formset_wrapper"),
                        lastRow = parentWrapper.find("tr:last"),
                        totalFormField = parentWrapper.find(
                            `input[name="${formPrefix}-TOTAL_FORMS"]`
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
