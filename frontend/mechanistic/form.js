import _ from "lodash";
import h from "shared/utils/helpers";

import $ from "$";

const experimentFormStartup = function (form) {
	$(form).find("#id_name").focus();
};

const chemicalFormStartup = function (f) {
	let form = $(f);

	h.setupOtherShowHideRelationship(
		form.find("select[name$='-composition_purity']"),
		form.find("input[name$='-composition_purity_other']"),
		"OT"
	);
};

export default document => {
    document.body.addEventListener("htmx:load", e => {
        if (e.target.querySelector(".form-experiment")) {
            experimentFormStartup(e.target);
		} else if (e.target.querySelector(".form-chemical")) {
            chemicalFormStartup(e.target);
		} else {
			// ...
		}
    });
};
