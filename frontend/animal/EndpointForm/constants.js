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
    };

export {termUrlLookup, textUrlLookup};
