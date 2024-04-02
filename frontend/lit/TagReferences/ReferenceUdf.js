import _ from "lodash";
import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {useEffect} from "react";
import HAWCUtils from "shared/utils/HAWCUtils";

const resetDynamicForm = function(formSelector, values, errors) {
        const root = $(formSelector);
        if (root.length === 0) {
            return;
        }

        // clear the entire form of existing data
        root[0].reset();

        // add data to form
        _.forEach(values, function(value, name) {
            _.forEach(value, function(val) {
                const input = root.find(`[name="${name}"]`);
                if (input.prop("multiple")) {
                    input.children(`option[value="${val}"]`).prop("selected", true);
                } else {
                    switch (input.prop("type")) {
                        case "radio":
                        case "checkbox":
                            input.each(function() {
                                // multiple select checkbox
                                if ($(this).attr("value") == val) {
                                    $(this).attr("checked", val);
                                }
                                // single checkbox
                                else if (
                                    $(this).attr("value") == undefined &&
                                    (val == "on" || val == true)
                                ) {
                                    $(this).attr("checked", true);
                                }
                            });
                            break;
                        default:
                            // text/number fields
                            input.val(val);
                    }
                }
            });
        });
        HAWCUtils.dynamicFormListeners();
        root.find(".invalid-feedback").remove();
        root.find(".is-invalid").removeClass("is-invalid");
        root.find(".bg-pink").removeClass("bg-pink");
        _.forEach(_.fromPairs(errors), function(error, field) {
            const input = root.find(`[name="${field}"]`);
            input.addClass("is-invalid");
            input
                .closest("div.form-group")
                .append(`<div class="invalid-feedback d-block">${error.join(" ")}</div>`);
            input
                .closest('[id^="collapse-"]')
                .siblings('[id^="udf-header-"]')
                .addClass("bg-pink");
        });
    },
    ReferenceUdf = inject("store")(
        observer(({currentUDF, UDFValues, UDFError}) => {
            useEffect(() => resetDynamicForm("#udf-forms", UDFValues, UDFError));
            if (!currentUDF) {
                return null;
            }
            return (
                <form id="udf-forms">
                    <div dangerouslySetInnerHTML={{__html: currentUDF}} />
                </form>
            );
        })
    );
ReferenceUdf.propTypes = {
    currentUDF: PropTypes.string.isRequired,
    UDFValues: PropTypes.object.isRequired,
    UDFError: PropTypes.array,
};

export default ReferenceUdf;
