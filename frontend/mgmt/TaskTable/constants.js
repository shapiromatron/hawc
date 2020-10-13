const STATUS = {
        10: {color: "#CFCFCF" /* grey */, type: "not started"},
        20: {color: "#FFCC00" /* yellow */, type: "started"},
        30: {color: "#00CC00" /* green */, type: "completed"},
        40: {color: "#CC3333" /* red */, type: "abandoned"},
    },
    TASK_TYPES = {
        10: "Data preparation",
        20: "Data extraction",
        30: "QA/QC",
        40: "Risk of bias/study evaluation completed",
    },
    TASK_TYPE_DESCRIPTIONS = {
        10: "Content which should be extracted from reference is clarified and saved to the Study instance for data-extractors.",
        20: "Data is extracted from reference into HAWC. This can be animal bioassay, epidemiological, epidemiological meta-analyses, or in-vitro data.",
        30: "Data extracted has been QA/QC.",
        40: "Risk of bias/study evaluation has been completed for this reference (if enabled for this assessment).",
    },
    STUDY_TYPES = {
        bioassay: "Animal bioassay",
        epi: "Epidemiology",
        epi_meta: "Epidemiology meta-analysis",
        in_vitro: "In vitro",
    };

export {STATUS, TASK_TYPES, TASK_TYPE_DESCRIPTIONS, STUDY_TYPES};
