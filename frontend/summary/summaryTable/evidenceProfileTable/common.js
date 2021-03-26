const NO_JUDGEMENT = 900,
    CUSTOM_JUDGEMENT = 910,
    HELP_TEXT = {
        JUDGEMENT: `If there are multiple finding rows, and judgments are merged, a single response is presented for all findings. Otherwise, each finding row will have it's own judgment and rationale.`,
        HIDE_CONTENT: "Do not present this section in the evidence profile table.",
        NO_CONTENT: "Text to display when there are no finding rows.",
        SECTION_SUBHEADING: `Generally, this text should not be changed unless the assessed evidence is a subset (e.g., focused on exposure only during development or via a specific route)`,
        IRIS_HANDBOOK: `See Chapter 11 in the EPA IRIS Handbook.`,
    };

export {NO_JUDGEMENT, CUSTOM_JUDGEMENT, HELP_TEXT};
