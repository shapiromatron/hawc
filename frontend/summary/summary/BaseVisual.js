import HAWCUtils from "shared/utils/HAWCUtils";
import h from "shared/utils/helpers";

import $ from "$";

import {addLabelAction} from "./common";

class BaseVisual {
    constructor(data) {
        this.data = data;
        this.data.created = new Date(this.data.created);
        this.data.last_updated = new Date(this.data.last_updated);
    }

    build_row(opts) {
        let arr = [
            `<a href="${this.data.url}">${this.data.title}</a>`,
            this.data.visual_type,
            HAWCUtils.truncateChars(this.data.caption),
            h.dateToString(this.data.created),
            h.dateToString(this.data.last_updated),
        ];
        if (opts.showPublished) {
            arr.splice(3, 0, HAWCUtils.booleanCheckbox(this.data.published));
        }
        return arr;
    }

    displayAsPage($el, options) {
        throw "Abstract method; requires implementation";
    }

    displayAsModal($el, options) {
        throw "Abstract method; requires implementation";
    }

    addActionsMenu() {
        return HAWCUtils.pageActionsButton([
            "Visualization editing",
            {href: this.data.url_update, text: "Update"},
            {href: this.data.url_delete, text: "Delete"},
            addLabelAction(this.data.label_htmx),
        ]);
    }

    object_hyperlink() {
        return $("<a>")
            .attr("href", this.data.url)
            .attr("target", "_blank")
            .text(this.data.title);
    }
}

export default BaseVisual;
