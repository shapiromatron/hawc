// Methods for attaching footnotes to any table
class TableFootnotes {
    constructor() {
        this.reset();
    }

    reset() {
        this.footnote_number = 97; // start at a
        this.footnotes = [];
    }

    add_footnote(texts) {
        // add a footnote and return the subscript for the footnote
        var keys = [],
            self = this;
        if (!(texts instanceof Array)) texts = [texts];
        texts.forEach(function (text) {
            var key;
            self.footnotes.forEach(function (v) {
                if (text === v.text) {
                    key = v.key;
                    return;
                }
            });
            if (key === undefined) {
                key = String.fromCharCode(self.footnote_number);
                self.footnotes.push({key, text});
                self.footnote_number += 1;
            }
            keys.push(key);
        });
        return `<sup>${keys.join(",")}</sup>`;
    }

    html_list() {
        // return an html formatted list of footnotes
        var list = [];
        this.footnotes.forEach(function (v, i) {
            list.push(`<sup>${v.key}</sup> ${v.text}`);
        });
        return list;
    }
}

export default TableFootnotes;
