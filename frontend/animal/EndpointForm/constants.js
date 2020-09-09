const termUrlLookup = {
        system_term_id: "/vocab/api/ehv/system/?format=json",
        organ_term_id: "/vocab/api/ehv/organ/?format=json",
        effect_term_id: "/vocab/api/ehv/effect/?format=json",
        effect_subtype_term_id: "/vocab/api/ehv/effect_subtype/?format=json",
        name_term_id: "/vocab/api/ehv/endpoint_name/?format=json",
    },
    textUrlLookup = {
        system_term_id: "/selectable/animal-endpointsystemlookup/?limit=100",
        organ_term_id: "/selectable/animal-endpointorganlookup/?limit=100",
        effect_term_id: "/selectable/animal-endpointeffectlookup/?limit=100",
        effect_subtype_term_id: "/selectable/animal-endpointeffectsubtypelookup/?limit=100",
        name_term_id: "/selectable/animal-endpointnamelookup/?limit=100",
    },
    label = {
        system: "System",
        organ: "Organ (and tissue)",
        effect: "Effect",
        effect_subtype: "Effect subtype",
        endpoint_name: "Endpoint/Adverse outcome*",
    },
    helpText = {
        system: "Relevant biological system",
        organ: "Relevant organ or tissue",
        effect: `Please reference terminology reference file and use Title Style. Commonly used
            effects include "Histopathology", "Malformation," "Growth", "Clinical Chemistry",
            "Mortality," "Organ Weight."`,
        effect_subtype: `Please reference terminology reference file and use Title Style. Commonly
            used effects include "Neoplastic", "Non-Neoplastic," "Feed Consumption",
            "Fetal Survival", "Body Weight," "Body Weight Gain," "Body Length". For
            Malformation effects, effect subtypes can be "Skeletal Malformation", "External
            Malformation" "Soft Tissue." For organ weight effects, subtypes can be "Absolute",
            "Relative" (absolute can be inferred when it's not explicitly stated).`,
        endpoint_name: `
            Short-text used to describe the endpoint/adverse outcome. As a first pass during
            extraction, use the endpoint name as presented in the study. Do not add units — units
            are summarized in a separate extraction field. Once extraction is complete for an
            assessment, endpoint/adverse outcomes names may be adjusted to use terms that best
            work across studies or assessments using the data clean-up tool (the original name as
            presented in the study will be retained in the "Endpoint Name in Study" field). If the
            endpoint is a repeated measure, then indicate the time in parentheses, e.g., running
            wheel activity (6 wk), using the abbreviated format: seconds = sec, minutes = min,
            hours = h, days = d, weeks = wk, months = mon, years = y.`,
    };

// TODO - change label/help-text to be epa/prime specific

export {termUrlLookup, textUrlLookup, label, helpText};
