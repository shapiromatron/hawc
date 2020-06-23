const BIO_STUDY_DESIGN = "bioassay-study-design",
    BIO_ENDPOINT = "bioassay-endpoint-summary",
    EPI_STUDY_DESIGN = "epidemiology-study-design",
    EPI_RESULT = "epidemiology-result-summary",
    OPTIONS = {
        [BIO_STUDY_DESIGN]: {
            AXIS_OPTIONS: [
                {
                    id: "dose-units",
                    label: "Dose units",
                    settings: [{column: "dose units", delimiter: "|", wrap_text: 0}],
                },
                {
                    id: "route-of-exposure",
                    label: "Route of exposure",
                    settings: [{column: "route of exposure", delimiter: "|", wrap_text: 0}],
                },
                {
                    id: "study-citation",
                    label: "Study citation",
                    settings: [{column: "study citation", delimiter: "", wrap_text: 0}],
                },
                {
                    id: "test-subject",
                    label: "Species & Sex",
                    settings: [
                        {column: "species", delimiter: "|", wrap_text: 0},
                        {column: "sex", delimiter: "|", wrap_text: 0},
                    ],
                },
                {
                    id: "study-design",
                    label: "Study design",
                    settings: [{column: "experiment type", delimiter: "|", wrap_text: 0}],
                },
                {
                    id: "system",
                    label: "System",
                    settings: [{column: "system", delimiter: "|", wrap_text: 0}],
                },
            ],
            FILTER_OPTIONS: [
                {
                    id: "study-citation",
                    label: "study citation",
                    settings: {column: "study citation", delimiter: "", on_click_event: "study"},
                },
                {
                    id: "system",
                    label: "system",
                    settings: {
                        column: "system",
                        delimiter: "|",
                        on_click_event: "endpoint_complete",
                    },
                },
                {
                    id: "organ",
                    label: "organ",
                    settings: {
                        column: "organ",
                        delimiter: "|",
                        on_click_event: "endpoint_complete",
                    },
                },
                {
                    id: "effect",
                    label: "effect",
                    settings: {
                        column: "effect",
                        delimiter: "|",
                        on_click_event: "endpoint_complete",
                    },
                },
            ],
            TABLE_FIELDS: [
                {column: "study citation", delimiter: "", on_click_event: "study"},
                {column: "system", delimiter: "|", on_click_event: "---"},
                {column: "dose units", delimiter: "|", on_click_event: "---"},
            ],
            DASHBOARDS: [
                {
                    id: "bio-sd-system-vs-study-design",
                    label: "system vs. study design",
                    x_axis: "study-design",
                    y_axis: "system",
                    filters: ["study-citation", "effect"],
                },
                {
                    id: "bio-sd-system-vs-test-subject",
                    label: "system vs. test subject",
                    x_axis: "test-subject",
                    y_axis: "system",
                    filters: ["study-citation", "effect"],
                },
                {
                    id: "bio-sd-dose-units-vs-route",
                    label: "dose units vs. route of exposure",
                    x_axis: "dose-units",
                    y_axis: "route-of-exposure",
                    filters: ["study-citation"],
                },
            ],
        },
        [BIO_ENDPOINT]: {
            AXIS_OPTIONS: [
                {
                    id: "test-subject",
                    label: "Species & Sex",
                    settings: [
                        {column: "species", delimiter: "", wrap_text: 0},
                        {column: "sex", delimiter: "", wrap_text: 0},
                    ],
                },
                {
                    id: "study-design",
                    label: "Study design",
                    settings: [{column: "experiment type", delimiter: "", wrap_text: 0}],
                },
                {
                    id: "system",
                    label: "System",
                    settings: [{column: "system", delimiter: "", wrap_text: 0}],
                },
            ],
            FILTER_OPTIONS: [
                {
                    id: "study-citation",
                    label: "study citation",
                    settings: {column: "study citation", delimiter: "", on_click_event: "study"},
                },
                {
                    id: "system",
                    label: "system",
                    settings: {
                        column: "system",
                        delimiter: "",
                        on_click_event: "endpoint_complete",
                    },
                },
                {
                    id: "organ",
                    label: "organ",
                    settings: {column: "organ", delimiter: "", on_click_event: "endpoint_complete"},
                },
                {
                    id: "effect",
                    label: "effect",
                    settings: {
                        column: "effect",
                        delimiter: "|",
                        on_click_event: "endpoint_complete",
                    },
                },
            ],
            TABLE_FIELDS: [
                {column: "study citation", delimiter: "", on_click_event: "study"},
                {column: "experiment name", delimiter: "", on_click_event: "experiment"},
                {column: "species", delimiter: "", on_click_event: "animal_group"},
                {column: "strain", delimiter: "", on_click_event: "---"},
                {column: "system", delimiter: "", on_click_event: "---"},
                {column: "organ", delimiter: "", on_click_event: "---"},
                {column: "effect", delimiter: "", on_click_event: "---"},
                {column: "endpoint name", delimiter: "", on_click_event: "endpoint_complete"},
            ],
            DASHBOARDS: [
                {
                    id: "bio-ep-system-vs-test-subject",
                    label: "system vs. test subject",
                    x_axis: "test-subject",
                    y_axis: "system",
                    filters: ["study-citation", "organ", "effect"],
                },
            ],
        },
        [EPI_STUDY_DESIGN]: {
            AXIS_OPTIONS: [
                {
                    id: "exposure",
                    label: "Exposure",
                    settings: [{column: "exposure name", delimiter: "|", wrap_text: 0}],
                },
                {
                    id: "study-design",
                    label: "Study design",
                    settings: [{column: "study design", delimiter: "|", wrap_text: 0}],
                },
                {
                    id: "system+effect",
                    label: "System & Effect",
                    settings: [
                        {column: "system", delimiter: "|", wrap_text: 0},
                        {column: "effect", delimiter: "|", wrap_text: 0},
                    ],
                },
            ],
            FILTER_OPTIONS: [
                {
                    id: "study-citation",
                    label: "study citation",
                    settings: {column: "study citation", delimiter: "", on_click_event: "study"},
                },
            ],
            TABLE_FIELDS: [
                {column: "study citation", delimiter: "", on_click_event: "study"},
                {column: "exposure name", delimiter: "|", on_click_event: "---"},
                {column: "system", delimiter: "|", on_click_event: "---"},
                {column: "effect", delimiter: "|", on_click_event: "---"},
            ],
            DASHBOARDS: [
                {
                    id: "epi-sd-study-design-vs-effect",
                    label: "study design vs. effect",
                    x_axis: "study-design",
                    y_axis: "system+effect",
                    filters: ["study-citation"],
                },
                {
                    id: "epi-sd-exposure-vs-effect",
                    label: "exposure vs. effect",
                    x_axis: "exposure",
                    y_axis: "system+effect",
                    filters: ["study-citation"],
                },
            ],
        },
        [EPI_RESULT]: {
            AXIS_OPTIONS: [
                {
                    id: "exposure",
                    label: "Exposure",
                    settings: [{column: "exposure name", delimiter: "", wrap_text: 0}],
                },
                {
                    id: "study-design",
                    label: "Study design",
                    settings: [{column: "study design", delimiter: "", wrap_text: 0}],
                },
                {
                    id: "system+effect",
                    label: "System & Effect",
                    settings: [
                        {column: "system", delimiter: "", wrap_text: 0},
                        {column: "effect", delimiter: "", wrap_text: 0},
                    ],
                },
            ],
            FILTER_OPTIONS: [
                {
                    id: "study-citation",
                    label: "study citation",
                    settings: {column: "study citation", delimiter: "", on_click_event: "study"},
                },
            ],
            TABLE_FIELDS: [
                {column: "study citation", delimiter: "", on_click_event: "study"},
                {column: "exposure name", delimiter: "", on_click_event: "exposure"},
                {column: "result name", delimiter: "", on_click_event: "result"},
            ],
            DASHBOARDS: [
                {
                    id: "epi-res-study-design-vs-effect",
                    label: "study design vs. effect",
                    x_axis: "study-design",
                    y_axis: "system+effect",
                    filters: ["study-citation"],
                },
                {
                    id: "epi-res-exposure-effect",
                    label: "exposure vs. effect",
                    x_axis: "exposure",
                    y_axis: "system+effect",
                    filters: ["study-citation"],
                },
            ],
        },
    };

export {OPTIONS};
