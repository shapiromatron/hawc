const DC_BIO_SD = "bioassay-study-design",
    DC_BIO_EP = "bioassay-endpoint-summary",
    DC_EPI_SD = "epidemiology-study-design",
    DC_EPI_RE = "epidemiology-result-summary",
    DATA_CLASSES = [DC_BIO_SD, DC_BIO_EP, DC_EPI_SD, DC_EPI_RE],
    AXIS_OPTIONS = [
        {
            data_classes: [DC_BIO_SD],
            id: "dose-units",
            label: "Dose units",
            settings: [{column: "dose units", delimiter: "|", wrap_text: 0}],
        },
        {
            data_classes: [DC_BIO_SD],
            id: "route-of-exposure",
            label: "Route of exposure",
            settings: [{column: "route of exposure", delimiter: "|", wrap_text: 0}],
        },
        {
            data_classes: [DC_BIO_SD],
            id: "study-citation",
            label: "Study citation",
            settings: [{column: "study citation", delimiter: "", wrap_text: 0}],
        },
        {
            data_classes: [DC_BIO_EP],
            id: "species-sex",
            label: "Species & Sex",
            settings: [
                {column: "species", delimiter: "", wrap_text: 0},
                {column: "sex", delimiter: "", wrap_text: 0},
            ],
        },
        {
            data_classes: [DC_BIO_EP],
            id: "system",
            label: "System",
            settings: [{column: "system", delimiter: "", wrap_text: 0}],
        },
    ],
    FILTER_OPTIONS = [
        {
            data_classes: [DC_BIO_SD, DC_BIO_EP, DC_EPI_SD, DC_EPI_RE],
            id: "study-citation",
            label: "study citation",
            settings: {column: "study citation", delimiter: "", on_click_event: "study"},
        },
        {
            data_classes: [DC_BIO_SD, DC_BIO_EP],
            id: "system",
            label: "system",
            settings: {column: "system", delimiter: "|", on_click_event: "endpoint_complete"},
        },
        {
            data_classes: [DC_BIO_SD, DC_BIO_EP],
            id: "organ",
            label: "organ",
            settings: {column: "organ", delimiter: "|", on_click_event: "endpoint_complete"},
        },
        {
            data_classes: [DC_BIO_SD, DC_BIO_EP],
            id: "effect",
            label: "effect",
            settings: {column: "effect", delimiter: "|", on_click_event: "endpoint_complete"},
        },
    ],
    TABLE_FIELDS = {
        [DC_BIO_SD]: [
            {column: "study citation", delimiter: "", on_click_event: "study"},
            {column: "system", delimiter: "|", on_click_event: "---"},
            {column: "dose units", delimiter: "|", on_click_event: "---"},
        ],
        [DC_BIO_EP]: [
            {column: "study citation", delimiter: "", on_click_event: "study"},
            {column: "experiment name", delimiter: "", on_click_event: "experiment"},
            {column: "species", delimiter: "", on_click_event: "animal_group"},
            {column: "strain", delimiter: "", on_click_event: "---"},
            {column: "system", delimiter: "", on_click_event: "---"},
            {column: "organ", delimiter: "", on_click_event: "---"},
            {column: "effect", delimiter: "", on_click_event: "---"},
            {column: "endpoint name", delimiter: "", on_click_event: "endpoint_complete"},
        ],
        [DC_EPI_SD]: [{column: "study citation", delimiter: "", on_click_event: "study"}],
        [DC_EPI_RE]: [{column: "study citation", delimiter: "", on_click_event: "study"}],
    },
    DASHBOARDS = [
        {
            data_class: DC_BIO_SD,
            id: "bioassay-dose-units",
            label: "dose units",
            x_axis: "dose-units",
            y_axis: "study-citation",
            filters: [],
        },
        {
            data_class: DC_BIO_SD,
            id: "bioassay-dose-units-route",
            label: "dose units by route of exposure",
            x_axis: "dose-units",
            y_axis: "route-of-exposure",
            filters: ["study-citation"],
        },
        {
            data_class: DC_BIO_EP,
            id: "bioassay-endpoint-system",
            label: "dose units by route of exposure",
            x_axis: "species-sex",
            y_axis: "system",
            filters: ["study-citation", "organ", "effect"],
        },
    ];

export {DATA_CLASSES, AXIS_OPTIONS, FILTER_OPTIONS, TABLE_FIELDS, DASHBOARDS};
