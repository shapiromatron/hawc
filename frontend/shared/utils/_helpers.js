export const addOuterTag = function(html, tag) {
    // if the html's outermost tag is not the given tag, add it
    // otherwise return the original html
    let regex = /^\s*<(.*)>.*<\/\1>\s*$/,
        match = html.match(regex);
    return match == null || match[1] != tag ? `<${tag}>${html}</${tag}>` : html;
};
