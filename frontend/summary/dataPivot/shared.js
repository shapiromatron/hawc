import _ from "lodash";

export const NULL_CASE = "---",
    OrderChoices = {
        asc: "asc",
        desc: "desc",
        custom: "custom",
    },
    buildStyleMap = cf => {
        // make mapping of current settings based on saved data pivot state
        return new Map(
            _.chain(cf.discrete_styles)
                .map(v => [v.key.toString(), v.style])
                .value()
        );
    };
