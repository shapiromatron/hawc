export const addOuterTag = function (html, tag) {
    // if the html's outermost tag is not the given tag, add it
    // otherwise return the original html
    let regex = /^\s*<(.*)>.*<\/\1>\s*$/,
        match = html.match(regex);
    return match == null || match[1] != tag ? `<${tag}>${html}</${tag}>` : html;
};

export const escapeRegex = function (text) {
    // Escape text containing regex special characters.
    // Lifted from https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Regular_expressions#escaping
    return text.replace(/[.+?^${}()|[\]\\]/g, "\\$&");
};

export const markKeywords = function (text, allSettings) {
    const all_tokens = allSettings.set1.keywords
            .concat(allSettings.set2.keywords)
            .concat(allSettings.set3.keywords),
        all_re = new RegExp(
            "\\b"
                .concat(
                    escapeRegex(all_tokens.join("WORD-JOIN-HERE"))
                        .replace(/WORD-JOIN-HERE/gm, "\\b|\\b")
                        .replace(/\*/g, "[\\S]*?")
                )
                .concat("\\b"),
            "gim"
        );
    if (all_tokens.length === 0) {
        return text;
    }
    text = text.replace(all_re, match => `<mark>${match}</mark>`);
    text = markText(text, allSettings.set1);
    text = markText(text, allSettings.set2);
    text = markText(text, allSettings.set3);
    return text;
};

export const markText = function (text, settings) {
    if (settings.keywords.length === 0) {
        return text;
    }
    const re = new RegExp(
        `<mark>(?<token>\\b${escapeRegex(settings.keywords.join("WORD-JOIN-HERE"))
            .replace(/WORD-JOIN-HERE/gm, "\\b|\\b")
            .replace(/\*/g, "[\\S]*?")}\\b)</mark>`,
        "gim"
    );
    return text.replace(
        re,
        (_match, token) =>
            `<mark class="hawc-mk" title="${settings.name}" style="border-bottom: 1px solid ${settings.color}; box-shadow: inset 0 -4px 0 ${settings.color};">${token}</mark>`
    );
};
