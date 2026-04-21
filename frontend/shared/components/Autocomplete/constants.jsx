import h from "shared/utils/helpers";

const DEFAULT_MIN_SEARCH_LENGTH = 3,
    DEBOUNCE_MS = 1000,
    theme = {
        container: "autocomplete__container",
        containerOpen: "autocomplete__container--open",
        input: "autocomplete__input",
        suggestionsContainer: "autocomplete__suggestions-container",
        suggestionsList: "autocomplete__suggestions-list",
        suggestion: "autocomplete__suggestion",
        suggestionHighlighted: "autocomplete__suggestion--highlighted",
        sectionContainer: "autocomplete__section-container",
        sectionTitle: "autocomplete__section-title",
    },
    boldPatternText = function (text, pattern) {
        const regex = new RegExp(h.escapeRegexString(pattern), "gi");
        return text.replace(regex, match => `<b>${match}</b>`);
    };

export {boldPatternText, DEBOUNCE_MS, DEFAULT_MIN_SEARCH_LENGTH, theme};
