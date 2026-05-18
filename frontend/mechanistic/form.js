import _ from "lodash";
import h from "shared/utils/helpers";

import $ from "$";

const experimentFormStartup = function (form) {
    $(form).find("#id_name").focus();
};

const chemicalFormStartup = function (f) {
    h.setupOtherShowHideRelationship(
        form.find("select[name='composition_purity']"),
        form.find("input[name='composition_purity_other']"),
        "OT"
    );
};

const testSystemFormStartup = function (f) {
    let form = $(f);

    h.setupOtherShowHideRelationship(
        form.find("select[name$='-test_system_type']"),
        form.find("input[name$='-test_system_type_other']"),
        "OTH"
    );

    /*
	// we don't seem to have an async way of getting back an updated species list.
	// other HAWC forms require users to manually refresh after adding a new one;
	// we'll stay consistent with that pattern.
	$("a[title='Create species']").on(window.app.HAWCUtils.HAWC_NEW_WINDOW_POPUP_CLOSING, function(e) {
		console.log("CLOSE IT!");
	});
	*/
};

const testDesignFormStartup = function (f) {
    let form = $(f);

    h.setupOtherShowHideRelationship(
        form.find("select[name$='-vehicle']"),
        form.find("input[name$='-vehicle_other']"),
        "OTHR"
    );

    h.setupOtherShowHideRelationship(
        form.find("select[name$='-final_concentration_vehicle']"),
        form.find("input[name$='-final_concentration_vehicle_other']"),
        "OTH"
    );

    /*
	// we don't seem to have an async way of getting back an updated species list.
	// other HAWC forms require users to manually refresh after adding a new one;
	// we'll stay consistent with that pattern.
	$("a[title='Create species']").on(window.app.HAWCUtils.HAWC_NEW_WINDOW_POPUP_CLOSING, function(e) {
		console.log("CLOSE IT!");
	});
	*/
};

export default document => {
    document.body.addEventListener("htmx:load", e => {
        if (e.target.querySelector(".form-experiment")) {
            experimentFormStartup(e.target);
        } else if (e.target.querySelector(".form-testsystem")) {
            testSystemFormStartup(e.target);
        } else if (e.target.querySelector(".form-testdesign")) {
            testDesignFormStartup(e.target);
        } else {
            console.log("OTHER CASE:");
            console.log(e.target);
        }
    });

    $(document).ready(function () {
        if ($("form#form-mech-chemical").length == 1) {
            chemicalFormStartup("form#form-mech-chemical");
        }
    });
};
