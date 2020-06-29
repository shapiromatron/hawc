const BIO_STUDY_DESIGN = "bioassay-study-design",
    BIO_ENDPOINT = "bioassay-endpoint-summary",
    BIO_ENDPOINT_DOSES = "bioassay-endpoint-doses-summary",
    EPI_STUDY_DESIGN = "epidemiology-study-design",
    EPI_RESULT = "epidemiology-result-summary",
    OPTIONS = {
        [BIO_STUDY_DESIGN]: {
            AXIS_OPTIONS: [
                {
                    id: "study-citation",
                    label: "Study citation",
                    settings: [{column: "study citation", delimiter: "", wrap_text: 0}],
                },
                {
                    id: "dose-units",
                    label: "Dose units",
                    settings: [{column: "dose units", delimiter: "|", wrap_text: 0}],
                },
                {
                    id: "experiment-type",
                    label: "Study design",
                    settings: [{column: "experiment type", delimiter: "|", wrap_text: 0}],
                },
                {
                    id: "route-of-exposure",
                    label: "Route of exposure",
                    settings: [{column: "route of exposure", delimiter: "|", wrap_text: 0}],
                },
                {
                    id: "chemical",
                    label: "Chemical",
                    settings: [{column: "experiment chemical", delimiter: "|", wrap_text: 0}],
                },
                {
                    id: "species-sex",
                    label: "Species & Sex",
                    settings: [
                        {column: "species", delimiter: "|", wrap_text: 0},
                        {column: "sex", delimiter: "|", wrap_text: 0},
                    ],
                },
                {
                    id: "species-strain",
                    label: "Species & Strain",
                    settings: [
                        {column: "species", delimiter: "|", wrap_text: 0},
                        {column: "strain", delimiter: "|", wrap_text: 0},
                    ],
                },
                {
                    id: "system",
                    label: "System",
                    settings: [{column: "system", delimiter: "|", wrap_text: 0}],
                },
                {
                    id: "organ",
                    label: "Organ",
                    settings: [{column: "organ", delimiter: "|", wrap_text: 0}],
                },
                {
                    id: "effect",
                    label: "Effect",
                    settings: [{column: "effect", delimiter: "|", wrap_text: 0}],
                },
            ],
            FILTER_OPTIONS: [
                {
                    id: "study-citation",
                    label: "study citation",
                    settings: {
                        column: "study citation",
                        delimiter: "",
                        on_click_event: "study",
                    },
                },
                {
                    id: "study-identifier",
                    label: "study identifier",
                    settings: {
                        column: "study identifier",
                        delimiter: "",
                        on_click_event: "study",
                    },
                },
                {
                    id: "experiment-type",
                    label: "experiment type",
                    settings: {
                        column: "experiment type",
                        delimiter: "|",
                        on_click_event: "---",
                    },
                },
                {
                    id: "species",
                    label: "species",
                    settings: {
                        column: "species",
                        delimiter: "|",
                        on_click_event: "---",
                    },
                },
                {
                    id: "strain",
                    label: "strain",
                    settings: {
                        column: "strain",
                        delimiter: "|",
                        on_click_event: "---",
                    },
                },
                {
                    id: "route-of-exposure",
                    label: "route of exposure",
                    settings: {
                        column: "route of exposure",
                        delimiter: "|",
                        on_click_event: "---",
                    },
                },
                {
                    id: "experiment-chemical",
                    label: "experiment chemical",
                    settings: {
                        column: "experiment chemical",
                        delimiter: "|",
                        on_click_event: "---",
                    },
                },
                {
                    id: "sex",
                    label: "sex",
                    settings: {
                        column: "sex",
                        delimiter: "|",
                        on_click_event: "---",
                    },
                },
                {
                    id: "system",
                    label: "system",
                    settings: {
                        column: "system",
                        delimiter: "|",
                        on_click_event: "---",
                    },
                },
                {
                    id: "organ",
                    label: "organ",
                    settings: {
                        column: "organ",
                        delimiter: "|",
                        on_click_event: "---",
                    },
                },
                {
                    id: "effect",
                    label: "effect",
                    settings: {
                        column: "effect",
                        delimiter: "|",
                        on_click_event: "---",
                    },
                },
                {
                    id: "dose-units",
                    label: "dose units",
                    settings: {
                        column: "dose units",
                        delimiter: "|",
                        on_click_event: "---",
                    },
                },
            ],
            TABLE_FIELDS: [
                {
                    id: "study-citation",
                    label: "study citation",
                    settings: {
                        column: "study citation",
                        delimiter: "",
                        on_click_event: "study",
                    },
                },
                {
                    id: "study-identifier",
                    label: "study identifier",
                    settings: {
                        column: "study identifier",
                        delimiter: "",
                        on_click_event: "study",
                    },
                },
                {
                    id: "experiment-type",
                    label: "experiment type",
                    settings: {
                        column: "experiment type",
                        delimiter: "|",
                        on_click_event: "---",
                    },
                },
                {
                    id: "species",
                    label: "species",
                    settings: {
                        column: "species",
                        delimiter: "|",
                        on_click_event: "---",
                    },
                },
                {
                    id: "strain",
                    label: "strain",
                    settings: {
                        column: "strain",
                        delimiter: "|",
                        on_click_event: "---",
                    },
                },
                {
                    id: "route-of-exposure",
                    label: "route of exposure",
                    settings: {
                        column: "route of exposure",
                        delimiter: "|",
                        on_click_event: "---",
                    },
                },
                {
                    id: "experiment-chemical",
                    label: "experiment chemical",
                    settings: {
                        column: "experiment chemical",
                        delimiter: "|",
                        on_click_event: "---",
                    },
                },
                {
                    id: "sex",
                    label: "sex",
                    settings: {
                        column: "sex",
                        delimiter: "|",
                        on_click_event: "---",
                    },
                },
                {
                    id: "system",
                    label: "system",
                    settings: {
                        column: "system",
                        delimiter: "|",
                        on_click_event: "---",
                    },
                },
                {
                    id: "organ",
                    label: "organ",
                    settings: {
                        column: "organ",
                        delimiter: "|",
                        on_click_event: "---",
                    },
                },
                {
                    id: "effect",
                    label: "effect",
                    settings: {
                        column: "effect",
                        delimiter: "|",
                        on_click_event: "---",
                    },
                },
                {
                    id: "dose-units",
                    label: "dose units",
                    settings: {
                        column: "dose units",
                        delimiter: "|",
                        on_click_event: "---",
                    },
                },
            ],
            DASHBOARDS: [
                {
                    id: "bio-sd-system-vs-study-design",
                    label: "system vs. study design",
                    x_axis: "experiment-type",
                    y_axis: "system",
                    filters: ["study-citation", "effect"],
                    table_fields: ["study-citation", "system", "dose-units"],
                },
                {
                    id: "bio-sd-system-vs-test-subject",
                    label: "system vs. test subject",
                    x_axis: "species-sex",
                    y_axis: "system",
                    filters: ["study-citation", "effect"],
                    table_fields: ["study-citation", "system", "dose-units"],
                },
                {
                    id: "bio-sd-dose-units-vs-route",
                    label: "dose units vs. route of exposure",
                    x_axis: "dose-units",
                    y_axis: "route-of-exposure",
                    filters: ["study-citation"],
                    table_fields: ["study-citation", "system", "dose-units"],
                },
            ],
        },
        [BIO_ENDPOINT]: {
            AXIS_OPTIONS: [
                {
                    id: "study-citation",
                    label: "Study citation",
                    settings: [{column: "study citation", delimiter: "", wrap_text: 0}],
                },
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
                {
                    id: "study-design+system",
                    label: "Study design & system",
                    settings: [
                        {column: "experiment type", delimiter: "", wrap_text: 0},
                        {column: "system", delimiter: "", wrap_text: 0},
                    ],
                },
            ],
            FILTER_OPTIONS: [
                {
                    id: "study-citation",
                    label: "study citation",
                    settings: {column: "study citation", delimiter: "", on_click_event: "study"},
                },
                {
                    id: "experiment-type",
                    label: "experiment type",
                    settings: {column: "experiment type", delimiter: "", on_click_event: "---"},
                },
                {
                    id: "species",
                    label: "species",
                    settings: {column: "species", delimiter: "", on_click_event: "---"},
                },
                {
                    id: "sex",
                    label: "sex",
                    settings: {column: "sex", delimiter: "", on_click_event: "---"},
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
                {
                    id: "study-citation",
                    label: "study citation",
                    settings: {column: "study citation", delimiter: "", on_click_event: "study"},
                },
                {
                    id: "experiment-name",
                    label: "experiment name",
                    settings: {
                        column: "experiment name",
                        delimiter: "",
                        on_click_event: "experiment",
                    },
                },
                {
                    id: "animal-group-name",
                    label: "animal group name",
                    settings: {
                        column: "animal group name",
                        delimiter: "",
                        on_click_event: "animal_group",
                    },
                },
                {
                    id: "species",
                    label: "species",
                    settings: {column: "species", delimiter: "", on_click_event: "animal_group"},
                },
                {
                    id: "strain",
                    label: "strain",
                    settings: {column: "strain", delimiter: "", on_click_event: "---"},
                },
                {
                    id: "system",
                    label: "system",
                    settings: {column: "system", delimiter: "", on_click_event: "---"},
                },
                {
                    id: "organ",
                    label: "organ",
                    settings: {column: "organ", delimiter: "", on_click_event: "---"},
                },
                {
                    id: "effect",
                    label: "effect",
                    settings: {column: "effect", delimiter: "", on_click_event: "---"},
                },
                {
                    id: "endpoint-name",
                    label: "endpoint name",
                    settings: {
                        column: "endpoint name",
                        delimiter: "",
                        on_click_event: "endpoint_complete",
                    },
                },
            ],
            DASHBOARDS: [
                {
                    id: "system-vs-test-subject",
                    label: "system vs. test subject",
                    x_axis: "test-subject",
                    y_axis: "system",
                    filters: ["experiment-type", "study-citation", "effect"],
                    table_fields: [
                        "study-citation",
                        "experiment-name",
                        "animal-group-name",
                        "system",
                        "organ",
                        "effect",
                        "endpoint-name",
                    ],
                },
                {
                    id: "test-subject-vs-study-design-system",
                    label: "test subjects vs. study design & system",
                    x_axis: "test-subject",
                    y_axis: "study-design+system",
                    filters: ["study-citation", "organ", "effect"],
                    table_fields: [
                        "study-citation",
                        "experiment-name",
                        "animal-group-name",
                        "system",
                        "organ",
                        "effect",
                        "endpoint-name",
                    ],
                },
                {
                    id: "reference-vs-system",
                    label: "reference vs. system",
                    x_axis: "study-citation",
                    y_axis: "system",
                    filters: [],
                    table_fields: [
                        "study-citation",
                        "experiment-name",
                        "animal-group-name",
                        "system",
                        "organ",
                        "effect",
                        "endpoint-name",
                    ],
                },
                {
                    id: "reference-vs-study-design-system",
                    label: "reference vs. study design & system",
                    x_axis: "study-citation",
                    y_axis: "study-design+system",
                    filters: [],
                    table_fields: [
                        "study-citation",
                        "experiment-name",
                        "animal-group-name",
                        "system",
                        "organ",
                        "effect",
                        "endpoint-name",
                    ],
                },
            ],
        },
        [BIO_ENDPOINT_DOSES]: {
            AXIS_OPTIONS: [
                {
                    id: "study-citation",
                    label: "Study citation",
                    settings: [{column: "study citation", delimiter: "", wrap_text: 0}],
                },
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
                {
                    id: "study-design+system",
                    label: "Study design & system",
                    settings: [
                        {column: "experiment type", delimiter: "", wrap_text: 0},
                        {column: "system", delimiter: "", wrap_text: 0},
                    ],
                },
            ],
            FILTER_OPTIONS: [
                {
                    id: "dose-units-name",
                    label: "dose units name",
                    settings: {column: "dose units name", delimiter: "", on_click_event: "---"},
                },
                {
                    id: "study-citation",
                    label: "study citation",
                    settings: {column: "study citation", delimiter: "", on_click_event: "study"},
                },
                {
                    id: "experiment-type",
                    label: "experiment type",
                    settings: {
                        column: "experiment type",
                        delimiter: "",
                        on_click_event: "experiment",
                    },
                },
                {
                    id: "species",
                    label: "species",
                    settings: {column: "species", delimiter: "", on_click_event: "animal_group"},
                },
                {
                    id: "sex",
                    label: "sex",
                    settings: {column: "sex", delimiter: "", on_click_event: "animal_group"},
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
                {
                    id: "study-citation",
                    label: "study citation",
                    settings: {column: "study citation", delimiter: "", on_click_event: "study"},
                },
                {
                    id: "experiment-name",
                    label: "experiment name",
                    settings: {
                        column: "experiment name",
                        delimiter: "",
                        on_click_event: "experiment",
                    },
                },
                {
                    id: "animal-group-name",
                    label: "animal group name",
                    settings: {
                        column: "animal group name",
                        delimiter: "",
                        on_click_event: "animal_group",
                    },
                },
                {
                    id: "species",
                    label: "species",
                    settings: {column: "species", delimiter: "", on_click_event: "animal_group"},
                },
                {
                    id: "strain",
                    label: "strain",
                    settings: {column: "strain", delimiter: "", on_click_event: "---"},
                },
                {
                    id: "system",
                    label: "system",
                    settings: {column: "system", delimiter: "", on_click_event: "---"},
                },
                {
                    id: "organ",
                    label: "organ",
                    settings: {column: "organ", delimiter: "", on_click_event: "---"},
                },
                {
                    id: "effect",
                    label: "effect",
                    settings: {column: "effect", delimiter: "", on_click_event: "---"},
                },
                {
                    id: "endpoint-name",
                    label: "endpoint name",
                    settings: {
                        column: "endpoint name",
                        delimiter: "",
                        on_click_event: "endpoint_complete",
                    },
                },
                {
                    id: "doses",
                    label: "doses",
                    settings: {column: "doses", delimiter: "", on_click_event: "---"},
                },
                {
                    id: "dose units name",
                    label: "dose units name",
                    settings: {column: "dose units name", delimiter: "", on_click_event: "---"},
                },
                {
                    id: "noel",
                    label: "noel",
                    settings: {column: "noel", delimiter: "", on_click_event: "---"},
                },
                {
                    id: "loel",
                    label: "loel",
                    settings: {column: "loel", delimiter: "", on_click_event: "---"},
                },
                {
                    id: "fel",
                    label: "fel",
                    settings: {column: "fel", delimiter: "", on_click_event: "---"},
                },
                {
                    id: "bmd",
                    label: "bmd",
                    settings: {column: "bmd", delimiter: "", on_click_event: "---"},
                },
                {
                    id: "bmdl",
                    label: "bmdl",
                    settings: {column: "bmdl", delimiter: "", on_click_event: "---"},
                },
            ],
            DASHBOARDS: [
                {
                    id: "system-vs-test-subject",
                    label: "system vs. test subject",
                    x_axis: "test-subject",
                    y_axis: "system",
                    filters: ["dose-units-name", "experiment-type", "study-citation", "effect"],
                    table_fields: [
                        "study-citation",
                        "experiment-name",
                        "animal-group-name",
                        "system",
                        "organ",
                        "effect",
                        "endpoint-name",
                        "doses",
                        "dose units name",
                        "noel",
                        "loel",
                        "bmd",
                        "bmdl",
                    ],
                },
                {
                    id: "test-subject-vs-study-design-system",
                    label: "test subjects vs. study design & system",
                    x_axis: "test-subject",
                    y_axis: "study-design+system",
                    filters: ["dose-units-name", "study-citation", "organ", "effect"],
                    table_fields: [
                        "study-citation",
                        "experiment-name",
                        "animal-group-name",
                        "system",
                        "organ",
                        "effect",
                        "endpoint-name",
                        "doses",
                        "dose units name",
                        "noel",
                        "loel",
                        "bmd",
                        "bmdl",
                    ],
                },
                {
                    id: "reference-vs-system",
                    label: "reference vs. system",
                    x_axis: "study-citation",
                    y_axis: "system",
                    filters: ["dose-units-name"],
                    table_fields: [
                        "study-citation",
                        "experiment-name",
                        "animal-group-name",
                        "system",
                        "organ",
                        "effect",
                        "endpoint-name",
                        "doses",
                        "dose units name",
                        "noel",
                        "loel",
                        "bmd",
                        "bmdl",
                    ],
                },
                {
                    id: "reference-vs-study-design-system",
                    label: "reference vs. study design & system",
                    x_axis: "study-citation",
                    y_axis: "study-design+system",
                    filters: ["dose-units-name"],
                    table_fields: [
                        "study-citation",
                        "experiment-name",
                        "animal-group-name",
                        "system",
                        "organ",
                        "effect",
                        "endpoint-name",
                        "doses",
                        "dose units name",
                        "noel",
                        "loel",
                        "bmd",
                        "bmdl",
                    ],
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
                {
                    id: "study-citation",
                    label: "study citation",
                    settings: {column: "study citation", delimiter: "", on_click_event: "study"},
                },
                {
                    id: "exposure-name",
                    label: "exposure name",
                    settings: {column: "exposure name", delimiter: "|", on_click_event: "---"},
                },
                {
                    id: "system",
                    label: "system",
                    settings: {column: "system", delimiter: "|", on_click_event: "---"},
                },
                {
                    id: "effect",
                    label: "effect",
                    settings: {column: "effect", delimiter: "|", on_click_event: "---"},
                },
            ],
            DASHBOARDS: [
                {
                    id: "epi-sd-study-design-vs-effect",
                    label: "study design vs. effect",
                    x_axis: "study-design",
                    y_axis: "system+effect",
                    filters: ["study-citation"],
                    table_fields: ["study-citation", "exposure-name", "system", "effect"],
                },
                {
                    id: "epi-sd-exposure-vs-effect",
                    label: "exposure vs. effect",
                    x_axis: "exposure",
                    y_axis: "system+effect",
                    filters: ["study-citation"],
                    table_fields: ["study-citation", "exposure-name", "system", "effect"],
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
                {
                    id: "study-citation",
                    label: "study citation",
                    settings: {column: "study citation", delimiter: "", on_click_event: "study"},
                },
                {
                    id: "exposure-name",
                    label: "exposure name",
                    settings: {column: "exposure name", delimiter: "", on_click_event: "exposure"},
                },
                {
                    id: "result-name",
                    label: "result name",
                    settings: {column: "result name", delimiter: "", on_click_event: "result"},
                },
            ],
            DASHBOARDS: [
                {
                    id: "epi-res-study-design-vs-effect",
                    label: "study design vs. effect",
                    x_axis: "study-design",
                    y_axis: "system+effect",
                    filters: ["study-citation"],
                    table_fields: ["study-citation", "exposure-name", "result-name"],
                },
                {
                    id: "epi-res-exposure-effect",
                    label: "exposure vs. effect",
                    x_axis: "exposure",
                    y_axis: "system+effect",
                    filters: ["study-citation"],
                    table_fields: ["study-citation", "exposure-name", "result-name"],
                },
            ],
        },
    };

export {OPTIONS};
