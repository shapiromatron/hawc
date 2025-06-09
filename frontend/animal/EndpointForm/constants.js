const termUrlLookupMap = {
        "system_term_id-1": "/vocab/api/ehv/system/?format=json",
        "organ_term_id-1": "/vocab/api/ehv/organ/?format=json",
        "effect_term_id-1": "/vocab/api/ehv/effect/?format=json",
        "effect_subtype_term_id-1": "/vocab/api/ehv/effect_subtype/?format=json",
        "name_term_id-1": "/vocab/api/ehv/endpoint_name/?format=json",
        "system_term_id-2": "/vocab/api/toxrefdb/system/?format=json",
        "organ_term_id-2": "/vocab/api/toxrefdb/organ/?format=json",
        "effect_term_id-2": "/vocab/api/toxrefdb/effect/?format=json",
        "effect_subtype_term_id-2": "/vocab/api/toxrefdb/effect_subtype/?format=json",
        "name_term_id-2": "/vocab/api/toxrefdb/endpoint_name/?format=json",
        "id-lookup-1": "/vocab/api/ehv/:id/endpoint-name-lookup/",
        "id-lookup-2": "/vocab/api/toxrefdb/:id/endpoint-name-lookup/",
    },
    termUrlLookup = function (term, vocab) {
        return termUrlLookupMap[`${term}-${vocab}`];
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
            system_popup: `The health effect category/biological system an endpoint/outcome or group of related endpoints/outcomes within a health effect category. "Multi-system" is an option for widespread effects. If the Endpoint is measured in Blood, Urine, or biological media other than the affected system, extract the media term in the Effect Subtype field.`,
            system: `The health effect category/biological system an endpoint/outcome or group of related endpoints/outcomes within a health effect category. Please use a controlled vocabulary term if possible.`,
            organ_popup: `Tissue should be used for same tissues affected in multiple organs/regions (e.g., epithelial, mesothelium). Region (e.g., head, abdomen, limb) are common for developmental endpoints. Multi-organ and Whole Body are options for widespread effects`,
            organ: `May also be tissue or region for developmental endpoints. Please use a controlled vocabulary term if possible.`,
            effect_popup: `A group of related outcomes considered as a health effect category and/or unit of analysis typically considered together during evidence synthesis.`,
            effect: `Related outcomes (e.g., unit of analysis) considered together during evidence synthesis. Please use a controlled vocabulary term if possible.`,
            effect_subtype_popup: `An outcome or measurement within an effect.`,
            effect_subtype: `Please use a controlled vocabulary term if possible.`,
            endpoint_name_popup: `An observable or measurable biological change used as an index of a potential health effect of an exposure. Endpoint may also be referred to as effect, outcome, or event. Search for the best match based on the author reported term. Use the field "Diagnostic (as reported)" to capture as reported by study authors. If no existing term matches, deselect use EHV for endpoint and enter the name as reported. Do not include units. If an endpoint is a repeated measure, indicate the time in parentheses, [e.g., running wheel activity (6 wk)], using the abbreviated format: seconds = sec, minutes = min, hours = h, days = d, weeks = wk, months = mon, years = y.`,
            endpoint_name: `An observable or measurable biological change used as an index of a potential health effect of an exposure. Endpoint may also be referred to as effect or outcome. For a searchable list of Environment Health Vocabulary terms, see the <a href="/vocab/ehv/">EHV.</a> Enter the term ID and all relationships to this term will automatically populate. Please use a controlled vocabulary term if possible.`,
        },
    },
    toxRefDBFields = {
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
            system_popup: `The health effect category/biological system an endpoint/outcome or group of related endpoints/outcomes within a health effect category. 'System' maps to 'endpoint_category' in ToxRefDB as the broadest descriptive term for an endpoint. Possible endpoint categories include: systemic, developmental, reproductive, and cholinesterase.`,
            system: `The health effect category/biological system an endpoint/outcome or group of related endpoints/outcomes within a health effect category. Please use a controlled vocabulary term if possible.`,
            effect_popup: `A group of related outcomes considered as a health effect category and/or unit of analysis typically considered together during evidence synthesis. 'Effect' maps to 'endpoint_type' in ToxRefDB as a subcategory for endpoint_category, which is more descriptive for a particular endpoint (e.g. pathology gross, clinical chemistry, reproductive performance, etc.`,
            effect: `Related outcomes (e.g., unit of analysis) considered together during evidence synthesis. Please use a controlled vocabulary term if possible.`,
            effect_subtype_popup: `An outcome or measurement within an effect. 'Effect_subtype' maps to 'Endpoint_target' in ToxRefDB indicating where or how the sample was collected to supply data for a particular endpoint. Typically describes an organ/tissue or metabolite/protein measured.`,
            effect_subtype: `Please use a controlled vocabulary term if possible.`,
            endpoint_name_popup: `An observable or measurable biological change used as an index of a potential health effect of an exposure. Endpoint may also be referred to as effect, outcome, or event. Search for the best match based on the author reported term. Use the field "Diagnostic (as reported)" to capture as reported by study authors. If no existing term matches, deselect use EHV for endpoint and enter the name as reported. Do not include units. If an endpoint is a repeated measure, indicate the time in parentheses, [e.g., running wheel activity (6 wk)], using the abbreviated format: seconds = sec, minutes = min, hours = h, days = d, weeks = wk, months = mon, years = y.`,
            endpoint_name: `An observable or measurable biological change used as an index of a potential health effect of an exposure. 'Endpoint_name' maps to 'Effect_desc' in ToxRefDB, detailing a specific condition associated with an endpoint_target (e.g. dysplasia, atrophy, necrosis, etc.`,
        },
    },
    defaultHelpText = {
        endpoint_name: `An observable or measurable biological change used as an index of a potential health effect of an exposure. Endpoint may also be referred to as effect or outcome. For a searchable list of terms, see the <a href="/vocab/ehv/">EHV</a> or <a href="/vocab/toxrefdb/">ToxRefDB</a>. Please use a controlled vocabulary term if possible.`,
    };

export {defaultHelpText, ehvFields, termUrlLookup, textUrlLookup, toxRefDBFields};
