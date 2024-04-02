import _ from "lodash";
import {observer} from "mobx-react";
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
                                if ($(this).attr("value") == val) {
                                    // multiple select checkbox
                                    $(this).attr("checked", val);
                                } else if (
                                    $(this).attr("value") == undefined &&
                                    (val == "on" || val == true)
                                ) {
                                    // single checkbox
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
    ReferenceUdf = observer(({store}) => {
        const {values, errors, formHtml} = store;

        useEffect(() => resetDynamicForm("#udf-forms", values, errors));

        if (formHtml.length === 0) {
            return null;
        }

        return (
            <form id="udf-forms">
                <div dangerouslySetInnerHTML={{__html: formHtml}} />
            </form>
        );
    });

ReferenceUdf.propTypes = {
    store: PropTypes.object.isRequired,
};

export default ReferenceUdf;
