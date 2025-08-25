import Quill from "quill";

const Inline = Quill.import("blots/inline");

class SmartTag extends Inline {
    static blotName = "smartTag";
    static tagName = "SPAN";
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

    format(name, value) {
        this.domNode.setAttribute("data-pk", value);
        this.domNode.setAttribute("data-type", value);
        super.format(name, value);
    }
}

Quill.register(SmartTag, true);

export default SmartTag;
