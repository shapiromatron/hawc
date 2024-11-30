import "quill/dist/quill.snow.css";

import Quill from "quill";
import SmartTag from "shared/smartTags/QuillSmartTag";
import SmartTagModal from "shared/smartTags/QuillSmartTagModal";
import SmartTagContainer from "shared/smartTags/SmartTagContainer";

import $ from "$";

Quill.register(SmartTag, true);
/* TODO - enable use of data attributes? */

const toolbarOptions = {
        container: [
            [{header: [false, 1, 2, 3, 4]}],
            ["bold", "italic", "underline", "strike"],
            [{script: "sub"}, {script: "super"}],
            [{color: []}, {background: []}],
            ["link", {list: "ordered"}, {list: "bullet"}, "blockquote"],
            ["smartTag"],
            ["clean"],
        ],
        handlers: {
            smartTag(value) {
                let sel = this.quill.getSelection();
                if (sel === null || sel.length === 0) {
                    window.alert("Select text to add a smart-tag.");
                    return;
                }
                this.quill.smartTagModal.showModal("smartTag", sel, value);
            },
        },
    },
    formatSmartTagButtons = function(q) {
        var tb = q.getModule("toolbar");
        $(tb.container)
            .find(".ql-smartTag")
            .append('<i class="fa fa-tag">');
        q.smartTagModal = new SmartTagModal(q, $("#smartTagModal"));
    },
    hideSmartTagButtons = function(q) {
        var tb = q.getModule("toolbar");
        $(tb.container)
            .find(".ql-smartTag")
            .hide();
    };

export default function() {
    let focusedItem = $(":focus"),
        modal = $("#smartTagModal"),
        showHawcTools = modal.length === 1;

    this.each(function() {
        let editor = document.createElement("div"),
            textarea = $(this),
            q;

        textarea.hide().before(editor);

        q = new Quill(editor, {
            modules: {toolbar: toolbarOptions},
            theme: "snow",
        });

        if (showHawcTools) {
            q.stc = new SmartTagContainer($(q.container).find(".ql-editor"));
            formatSmartTagButtons(q);
        } else {
            hideSmartTagButtons(q);
        }
        q.clipboard.dangerouslyPasteHTML(textarea.val());
        q.on("text-change", function(delta, oldDelta, source) {
            textarea.val(q.getSemanticHTML());
        });
        textarea.data("_quill", q);

        if (q.stc) {
            q.stc.enableModals();
        }
    });

    // restore original focus
    $(focusedItem).focus();
}
