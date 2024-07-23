const termUrlLookup = function(term, vocab_url) {
        const terms = {
            system_term_id: `/vocab/api/${vocab_url}/system/?format=json`,
            organ_term_id: `/vocab/api/${vocab_url}/organ/?format=json`,
            effect_term_id: `/vocab/api/${vocab_url}/effect/?format=json`,
            effect_subtype_term_id: `/vocab/api/${vocab_url}/effect_subtype/?format=json`,
            name_term_id: `/vocab/api/${vocab_url}/endpoint_name/?format=json`,
        };
        return terms[term];
    },
    textUrlLookup = {
        system_term_id: "/autocomplete/animal-endpointautocomplete/?field=system",
        organ_term_id: "/autocomplete/animal-endpointautocomplete/?field=organ",
        effect_term_id: "/autocomplete/animal-endpointautocomplete/?field=effect",
        effect_subtype_term_id: "/autocomplete/animal-endpointautocomplete/?field=effect_subtype",
        name_term_id: "/autocomplete/animal-endpointautocomplete/?field=name",
    },
    ehvFields = {
        label: {
            system: "System",
            organ: "Organ/Tissue/Region",
            effect: "Effect",
            effect_subtype: "Effect subtype",
            endpoint_name: "Endpoint/Adverse outcome*",
        },
        parent_id: {
            organ_parent: "system_term_id",
            effect_parent: "organ_term_id",
            effect_subtype_parent: "effect_term_id",
            endpoint_name_parent: "effect_subtype_term_id",
        },
        helpText: {
            system_popup: `The health effect category/biological system an endpoint/outcome or group of
            related endpoints/outcomes within a health effect category. "Multi-system" is an option for
            widespread effects. If the Endpoint is measured in Blood, Urine, or biological media other
            than the affected system, extract the media term in the Effect Subtype field.`,
            system: `The health effect category/biological system an endpoint/outcome or group of
            related endpoints/outcomes within a health effect category. Please use a controlled
            vocabulary term if possible.`,
            organ_popup: `Tissue should be used for same tissues affected in multiple organs/regions
            (e.g., epithelial, mesothelium). Region (e.g., head, abdomen, limb) are common for
            developmental endpoints. Multi-organ and Whole Body are options for widespread effects`,
            organ: `May also be tissue or region for developmental endpoints. Please use a controlled
            vocabulary term if possible.`,
            effect_popup: `A group of related outcomes considered as a health effect category and/or
            unit of analysis typically considered together during evidence synthesis.`,
            effect: `Related outcomes (e.g., unit of analysis) considered together during evidence
            synthesis. Please use a controlled vocabulary term if possible.`,
            effect_subtype_popup: `An outcome or measurement within an effect.`,
            effect_subtype: `Please use a controlled vocabulary term if possible.`,
            endpoint_name_popup: `An observable or measurable biological change used as an index of a
            potential health effect of an exposure. Endpoint may also be referred to as effect, outcome,
            or event. Search for the best match based on the author reported term. Use the
            field "Diagnostic (as reported)" to capture as reported by study authors. If no existing
            term matches, deselect use EHV for endpoint and enter the name as reported. Do not
            include units. If an endpoint is a repeated measure, indicate the time in parentheses,
            [e.g., running wheel activity (6 wk)], using the abbreviated format: seconds = sec,
            minutes = min, hours = h, days = d, weeks = wk, months = mon, years = y.`,
            endpoint_name: `An observable or measurable biological change used as an index of a
            potential health effect of an exposure. Endpoint may also be referred to as effect or
            outcome. For a searchable list of Environment Health Vocabulary terms, see the
            <a href="/vocab/ehv/">EHV.</a> Enter the term ID and all relationships to this term
            will automatically populate. Please use a controlled vocabulary term if possible.`,
        },
    },
    toxrefFields = {
        label: {
            system: "Endpoint Category",
            effect: "Endpoint Type",
            effect_subtype: "Endpoint Target",
            endpoint_name: "Effect Description",
        },
        parent_id: {
            effect_parent: "system_term_id",
            effect_subtype_parent: "effect_term_id",
            endpoint_name_parent: "effect_subtype_term_id",
        },
        helpText: {
            system_popup: `The health effect category/biological system an endpoint/outcome or group of
            related endpoints/outcomes within a health effect category. "Multi-system" is an option for
            widespread effects. If the Endpoint is measured in Blood, Urine, or biological media other
            than the affected system, extract the media term in the Effect Subtype field.`,
            system: `The health effect category/biological system an endpoint/outcome or group of
            related endpoints/outcomes within a health effect category. Please use a controlled
            vocabulary term if possible.`,
            organ_popup: `Tissue should be used for same tissues affected in multiple organs/regions
            (e.g., epithelial, mesothelium). Region (e.g., head, abdomen, limb) are common for
            developmental endpoints. Multi-organ and Whole Body are options for widespread effects`,
            organ: `May also be tissue or region for developmental endpoints. Please use a controlled
            vocabulary term if possible.`,
            effect_popup: `A group of related outcomes considered as a health effect category and/or
            unit of analysis typically considered together during evidence synthesis.`,
            effect: `Related outcomes (e.g., unit of analysis) considered together during evidence
            synthesis. Please use a controlled vocabulary term if possible.`,
            effect_subtype_popup: `An outcome or measurement within an effect.`,
            effect_subtype: `Please use a controlled vocabulary term if possible.`,
            endpoint_name_popup: `An observable or measurable biological change used as an index of a
            potential health effect of an exposure. Endpoint may also be referred to as effect, outcome,
            or event. Search for the best match based on the author reported term. Use the
            field "Diagnostic (as reported)" to capture as reported by study authors. If no existing
            term matches, deselect use EHV for endpoint and enter the name as reported. Do not
            include units. If an endpoint is a repeated measure, indicate the time in parentheses,
            [e.g., running wheel activity (6 wk)], using the abbreviated format: seconds = sec,
            minutes = min, hours = h, days = d, weeks = wk, months = mon, years = y.`,
            endpoint_name: `An observable or measurable biological change used as an index of a
            potential health effect of an exposure. Endpoint may also be referred to as effect or
            outcome. For a searchable list of ToxrefDB Vocabulary terms, see the
            <a href="/vocab/toxref/">ToxRef.</a> Enter the term ID and all relationships to this term
            will automatically populate. Please use a controlled vocabulary term if possible.`,
        },
    },
    defaultHelpText = {
        endpoint_name: `An observable or measurable biological change used as an index of a
        potential health effect of an exposure. Endpoint may also be referred to as effect or
        outcome. For a searchable list of Environment Health Vocabulary terms, see the
        <a href="/vocab/ehv/">EHV</a> and <a href="/vocab/toxref/">ToxRef</a>. Please use a controlled vocabulary term if possible.`,
    };

export {defaultHelpText, ehvFields, termUrlLookup, textUrlLookup, toxrefFields};
