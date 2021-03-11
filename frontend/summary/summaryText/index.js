export default function(cb) {
    import("./split.js").then(summaryText => {
        cb(summaryText.default);
    });
}
