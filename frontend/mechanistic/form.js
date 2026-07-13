import _ from "lodash";
import h from "shared/utils/helpers";

import $ from "$";

import startupEndpointForm from "../animal/EndpointForm";

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

	import("shared/components/JsonListWidget.js").then(function(module) {
		let widget = new module.default.widget_class();
		widget.initializeWidgetUi("concentrations_tested");
		// widget.initializeAllWidgetUis();
	});
};

const controlFormStartup = function (f) {
    let form = $(f);

    h.setupOtherShowHideRelationship(
        form.find("select[name$='-control_type']"),
        form.find("input[name$='-control_type_other']"),
        "OTH"
    );
};

const endpointFormStartup = function (f) {
    let form = $(f);

	// EHV kickoff - start
	let config = JSON.parse(form.find("#hxCustomContext_mechanisticendpoint").html());
	let vocabSettings = JSON.parse(config.vocabulary);
	
	startupEndpointForm(document.getElementById("vocabWidgets"), vocabSettings);

	// remove the effect/effect-subtype widgets; we don't use those on mechanistic right now
	setTimeout(function() {
		let ehvFields = ["name", "system", "organ", "effect", "effect_subtype"];
		for (let i = 0 ; i < ehvFields.length ; i++) {
			let ehvField = ehvFields[i];
			$("div[id^='div_id_endpoint-'][id$='-" + ehvField + "']").each(function() {
				// need to do two things actually:
				// 1. hide the default crispy UI; startupEndpointForm added other widgets/controls
				// 2. rename those UI things that startupEndpointForm  created; e.g.
				//    when editing endpoint #19, we'd want to rename the element "organ" that 
				//    startupEndpointForm created to "endpoint-19-organ".
				let ehvDiv = $(this);
				let actualPrefix = ehvDiv.attr("id").replace("div_id_", "").replace(ehvField, "");

				// thing 1
				$("input[type='hidden'][name='" + ehvField + "']").attr("name", actualPrefix + ehvField);
				$("input[type='hidden'][name='" + ehvField + "_term']").attr("name", actualPrefix + ehvField + "_term");

				// thing 2
				ehvDiv.remove();
				$("input[type='hidden'][id='id_" + actualPrefix + ehvField + "_term']").remove(); // the hidden widget(s) right before "remarks"...
			});
		}

		// hide effect/subtype -- the EHV system sort of assumes they are there, but we don't want
		// them in mechanistic...easiest route is just hide the widget, so they are alwauys blank in
		// the db. That way we don't have to muck with the existing term code
		$("div#vocabWidgets div.row div.col-md-3:eq(3)").remove();
		$("div#vocabWidgets div.row div.col-md-3:eq(2)").remove();

		// we hide this in CSS - and now once it's set up, we show it. This way, you don't see
		// effect/subtype blink out of visibility; you just see everything appear, which is nicer.
		// (why opacity? If using display:none instead of opacity: 0 in the css, then the page
		// scrolls to the top. Rather than track that down, just use opacity 0->1 which doesn't
		// have the same issue...)
		$("tr.mechanisticendpoint-edit-row").css("opacity", 1);
	}, 100);

	// EHV kickoff - end

    h.setupOtherShowHideRelationship(
        form.find("select[name$='-poa_process']"),
        form.find("input[name$='-poa_process_other']"),
        "OTHR"
    );

    h.setupOtherShowHideRelationship(
        form.find("select[name$='-poa_action']"),
        form.find("input[name$='-poa_action_other']"),
        "OTHR"
    );

	/*
	import("shared/components/JsonListWidget.js").then(function(module) {
		let widget = new module.default.widget_class();
		widget.initializeWidgetUi("poa");
		// widget.initializeAllWidgetUis();
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
        } else if (e.target.querySelector(".form-mechcontrol")) {
            controlFormStartup(e.target);
        } else if (e.target.querySelector(".form-mechanisticendpoint")) {
            endpointFormStartup(e.target);
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
