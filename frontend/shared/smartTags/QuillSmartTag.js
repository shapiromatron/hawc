import Quill from "quill";

const Inline = Quill.import("blots/inline");

class SmartTag extends Inline {
    static create(value) {
        let el = document.createElement("SPAN");
        el.setAttribute("class", "smart-tag active");
        el.dataset.pk = value.pk;
        el.dataset.type = value.type;
        return el;
    }

    static formats(domNode) {
        let cls = domNode.getAttribute("class") || "";
        if (cls.indexOf("smart-tag") < 0) {
            return null;
        }
        return {
            pk: parseInt(domNode.dataset.pk),
            type: domNode.dataset.type,
        };
    }
}
SmartTag.blotName = "smartTag";
SmartTag.tagName = "SPAN";

export default SmartTag;
