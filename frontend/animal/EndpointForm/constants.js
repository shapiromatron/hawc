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
    helpTextWithEhv = {
        system: `TODO`,
        organ: `TODO`,
        effect: `TODO`,
        effect_subtype: `TODO`,
        endpoint_name: `TODO`,
        endpoint_name_shortened: `TODO`,
    },
    helpTextNoEhv = {
        system: `The health effect category/biological system an endpoint/outcome or group of
            related endpoints/outcomes within a health effect category that are considered together
            belong to. Multi-system is an option for wide-spread effects. If the Endpoint is measured
            in Blood, Urine or biological media other than the affected system, it should be captured
            in the Effect Subtype field.`,
        organ: `Tissue should be used for same tissues affected in multiple organs/regions (e.g.,
            epithelial, mesothelium). Region (e.g., head, abdomen, limb) are common for
            developmental endpoints. Multi-organ and Whole Body are options for wide-spread effects`,
        effect: `A group of related endpoints/outcomes considered as a health effect category
            typically considered together during evidence synthesis.`,
        effect_subtype: `An endpoint/outcome or outcome measure within an effect.`,
        endpoint_name: `An observable or measurable biological change used as an index of a potential
            health effect of an exposure. Endpoint may also be referred to as effect or outcome.
            Search for the best match based on the author reported term. Use the field "Endpoint Name in Study"
            to capture as reported by study authors. If no existing term matches, deselect use EHV
            for endpoint and enter the name as reported. Do not add include units. If an endpoint is
            a repeated measure, indicate the time in parentheses, e.g., running wheel activity (6 wk),
            using the abbreviated format: seconds = sec, minutes = min, hours = h, days = d,
            weeks = wk, months = mon, years = y.`,
        endpoint_name_shortened: `An observable or measurable biological change of a potential
            health effect of an exposure.  Endpoint may also be referred to as effect or outcome.
            For a searchable list of Environment Health Vocabulary terms, see the <a href="/vocab/ehv/">EHV.</a>`,
    };

export {helpTextNoEhv, helpTextWithEhv, label, termUrlLookup, textUrlLookup};
