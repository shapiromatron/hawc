export const STATUS = {
        10: {color: "#CFCFCF", type: "not started"},
        20: {color: "#FFCC00", type: "started"},
        30: {color: "#00CC00", type: "completed"},
        40: {color: "#CC3333", type: "abandoned"},
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
    STUDY_TYPE_CHOICES = [
        {id: "bioassay", label: "Animal bioassay"},
        {id: "epi", label: "Epidemiology"},
        {id: "epi_meta", label: "Epidemiology meta-analysis"},
        {id: "in_vitro", label: "In vitro"},
        {id: "eco", label: "Ecology"},
    ];
