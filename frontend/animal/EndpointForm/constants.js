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
        system: `The health effect category/biological system an endpoint/outcome or group of 
            related endpoints/outcomes within a health effect category that are considered together 
            belong to. Please use a controlled vocabulary term if enabled for your assessment. 
            Multi-system is an option for wide-spread effects. If the Endpoint is measured in Blood, 
            Urine or biological media other than the affected system, it should be captured in the 
            Effect Subtype field. `,
        organ: `Please use a controlled vocabulary term if possible and if enabled for your assessment. 
            Tissue should be used for same tissues affected in multiple organs/regions (e.g., epithelial, 
            mesothelium). Region (e.g., head, abdomen, limb) are common for developmental endpoints. 
            Multi-organ and Whole Body are options for wide-spread effects`,
        effect: `A group of related endpoints/outcomes considered as a health effect category typically 
            considered together during evidence synthesis. Please use a controlled vocabulary term if 
            enabled for your assessment.`,
        effect_subtype: `An endpoint/outcome or outcome measure within an effect. Please use a 
            controlled vocabulary term if enabled for your assessment.`,
        endpoint_name: `An observable or measurable biological change used as an index of a potential health effect of 
            a chemical exposure. Often, “endpoint” is used when describing animal toxicological findings while 
            outcome” is used when describing human findings. Endpoint may also be referred to as effect. 
            Please use a controlled vocabulary term if possible and if enabled for your assessment. Search 
            the vocabulary for the best match based on the author reported term. Note there is a separate 
            field entitled, "Endpoint Name in Study", for optional capture of the endpoint name as reported 
            by the study author. If no preferred term matches the data extracted, deselect use EHV for endpoint 
            and type in the endpoint name as reported by study authors using HAWC data extraction annotation. 
            Do not add units — units are summarized in a separate extraction field. If the endpoint is a 
            repeated measure, indicate the time in parentheses, e.g., running wheel activity (6 wk), using 
            the abbreviated format: seconds = sec, minutes = min, hours = h, days = d, weeks = wk, 
            months = mon, years = y.`,
    };

export {helpText, label, termUrlLookup, textUrlLookup};
