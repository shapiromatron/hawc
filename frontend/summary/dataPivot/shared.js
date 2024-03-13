import _ from "lodash";
import h from "shared/utils/helpers";

export const NULL_CASE = "---",
    OrderChoices = {
        asc: "asc",
        desc: "desc",
        custom: "custom",
    },
    buildStyleMap = (cf, alwaysString) => {
        // make mapping of current settings based on saved data pivot state. We cast to
        // a string for the select input, but try to cast to numeric for comparisons.
        return new Map(
            _.chain(cf.discrete_styles)
                .map(v => [
                    alwaysString ? v.key.toString() : h.castNumberOrKeepString(v.key),
                    v.style,
                ])
                .value()
        );
    };
