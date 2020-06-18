const DC_BIO_SD = "bioassay-study-design",
    DC_BIO_EP = "bioassay-endpoint-summary",
    DC_EPI_SD = "epidemiology-study-design",
    DC_EPI_RE = "epidemiology-result-summary",
    DATA_CLASSES = [DC_BIO_SD, DC_BIO_EP, DC_EPI_SD, DC_EPI_RE],
    AXIS_OPTIONS = [
        {
            data_classes: [DC_BIO_EP],
            id: "species-sex",
            label: "Species & Sex",
            settings: [
                {column: "species", delimiter: ""},
                {column: "sex", delimiter: ""},
            ],
        },
        {
            data_classes: [DC_BIO_EP],
            id: "system",
            label: "System",
            settings: [{column: "system", delimiter: ""}],
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
            data_classes: [DC_BIO_EP],
            id: "system",
            label: "system",
            settings: {column: "system", delimiter: "", on_click_event: "endpoint_complete"},
        },
        {
            data_classes: [DC_BIO_EP],
            id: "organ",
            label: "organ",
            settings: {column: "organ", delimiter: "", on_click_event: "endpoint_complete"},
        },
        {
            data_classes: [DC_BIO_EP],
            id: "effect",
            label: "effect",
            settings: {column: "effect", delimiter: "", on_click_event: "endpoint_complete"},
        },
    ],
    TABLE_FIELDS = {
        [DC_BIO_SD]: [{column: "study citation", on_click_event: "study"}],
        [DC_BIO_EP]: [
            {column: "study citation", on_click_event: "study"},
            {column: "experiment name", on_click_event: "experiment"},
            {column: "species", on_click_event: "animal_group"},
            {column: "strain", on_click_event: "---"},
            {column: "system", on_click_event: "---"},
            {column: "organ", on_click_event: "---"},
            {column: "effect", on_click_event: "---"},
            {column: "endpoint name", on_click_event: "endpoint_complete"},
        ],
        [DC_EPI_SD]: [{column: "study citation", on_click_event: "study"}],
        [DC_EPI_RE]: [{column: "study citation", on_click_event: "study"}],
    };

export {DATA_CLASSES, AXIS_OPTIONS, FILTER_OPTIONS, TABLE_FIELDS};
