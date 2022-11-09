const termUrlLookup = {
        system_term_id: "/vocab/api/ehv/system/?format=json",
        organ_term_id: "/vocab/api/ehv/organ/?format=json",
        effect_term_id: "/vocab/api/ehv/effect/?format=json",
        effect_subtype_term_id: "/vocab/api/ehv/effect_subtype/?format=json",
        name_term_id: "/vocab/api/ehv/endpoint_name/?format=json",
    },
    textUrlLookup = {
        system_term_id: "/autocomplete/animal-endpointautocomplete/?field=system",
        organ_term_id: "/autocomplete/animal-endpointautocomplete/?field=organ",
        effect_term_id: "/autocomplete/animal-endpointautocomplete/?field=effect",
        effect_subtype_term_id: "/autocomplete/animal-endpointautocomplete/?field=effect_subtype",
        name_term_id: "/autocomplete/animal-endpointautocomplete/?field=name",
    },
    label = {
        system: "System",
        organ: "Organ/Tissue/Region",
        effect: "Effect",
        effect_subtype: "Effect subtype",
        endpoint_name: "Endpoint/Adverse outcome*",
    },
    helpText = {
        system: `The affected biological system. Please use a controlled vocabulary term if
            possible and if enabled for your assessment. Multi-system and Whole Body are options
            for wide-spread effects. If the Endpoint is measured in Blood, Urine or biological
            media other than the affected system, it should be captured in the Effect Subtype field. `,
        organ: `Please use a controlled vocabulary term if possible and if enabled for your
            assessment. Tissue should be used for same tissues affected in multiple organs/regions
            (e.g., epithelial, mesothelium). Region (e.g., head, abdomen, limb) are common for
            developmental endpoints. Multi-organ and Whole Body are options for wide-spread effects.`,
        effect: `Please use a controlled vocabulary term if possible and if enabled for your assessment
            (eg., Malformation, Neoplastic [Non-Neoplastic] Lesions, Organ Weight, Abnormal Appearance).`,
        effect_subtype: `The method used for the measuring the Effect (e.g., Histopathology,
            Clinical Observation, Clinical Chemistry, Hematology). For Developmental Malformation
            effects, values may be Skeletal Structural Abnormality, Skeletal Ossification
            Abnormality, External Abnormality, or Visceral Abnormality. For Organ Weights,
            may be Absolute or Relative (absolute can be inferred when it's not explicitly
            stated). When a determination cannot be made, use [Null] or leave empty.`,
        endpoint_name: `
            Short-text used to describe the data in this form. Please use a controlled vocabulary
            term if possible and if enabled for your assessment. A separate field,
            "Endpoint Name in Study", captures the name of endpoint as reported. If no preferred
            term matches the data extracted, type in the desired description. Do not add units — units
            are summarized in a separate extraction field.  If the endpoint is a repeated measure,
            indicate the time in parentheses, e.g., running wheel activity (6 wk), using the
            abbreviated format: seconds = sec, minutes = min, hours = h, days = d, weeks = wk,
            months = mon, years = y.`,
    };

export {helpText, label, termUrlLookup, textUrlLookup};
