import {beforeEach, describe, expect, it, vi} from "vitest";

// Global $ mock for the modules that require it
global.$ = {
    fn: {},
    prototype: {},
};

// Create a basic DOM structure for testing
beforeEach(() => {
    document.body.innerHTML = `
        <div id="smartTagModal" style="display: none;">
            <select id="id_resource">
                <option value="study">Study</option>
            </select>
            <select id="id_study">
                <option value="1">Test Study</option>
            </select>
        </div>
        <textarea class="quilltext" id="test-textarea">
            <p>Test content with <span class="smart-tag" data-type="study" data-pk="1">smart tag</span></p>
        </textarea>
    `;
});

describe("Quillify functionality", () => {
    it("should register SmartTag correctly", async () => {
        const SmartTag = (await import("shared/smartTags/QuillSmartTag")).default,
            smartTagEl = SmartTag.create({pk: 1, type: "study"});
        expect(smartTagEl.tagName).toBe("SPAN");
        expect(smartTagEl.dataset.pk).toBe("1");
        expect(smartTagEl.dataset.type).toBe("study");
        expect(smartTagEl.className).toContain("smart-tag");
    });

    it("should register SmartInline blots correctly", async () => {
        const SmartInline = (await import("shared/smartTags/QuillSmartInline")).default,
            smartInlineEl = SmartInline.create({pk: 2, type: "endpoint"});
        expect(smartInlineEl.tagName).toBe("DIV");
        expect(smartInlineEl.dataset.pk).toBe("2");
        expect(smartInlineEl.dataset.type).toBe("endpoint");
        expect(smartInlineEl.className).toContain("smart-tag");
    });

    it("should parse SmartTag format correctly", async () => {
        const SmartTag = (await import("shared/smartTags/QuillSmartTag")).default;

        // Create a DOM node that represents a smart tag
        const domNode = document.createElement("span");
        domNode.className = "smart-tag active";
        domNode.dataset.pk = "123";
        domNode.dataset.type = "study";

        const format = SmartTag.formats(domNode);
        expect(format).toEqual({
            pk: 123,
            type: "study",
        });

        // Test with non-smart-tag element
        const normalNode = document.createElement("span");
        normalNode.className = "normal-class";

        const nullFormat = SmartTag.formats(normalNode);
        expect(nullFormat).toBe(null);
    });

    it("should create Quill instance with custom toolbar including smart tag buttons", async () => {
        const Quill = (await import("quill")).default,
            toolbarOptions = (await import("shared/utils/Quillify")).toolbarOptions,
            editorDiv = document.createElement("div"),
            quill = new Quill(editorDiv, {modules: {toolbar: toolbarOptions}});

        document.body.appendChild(editorDiv);

        // Check that toolbar module exists
        const toolbar = quill.getModule("toolbar");
        expect(toolbar).toBeDefined();
        expect(toolbar.container).toBeDefined();

        // Check that smart tag buttons were created
        const smartTagBtn = toolbar.container.querySelector(".ql-smartTag"),
            smartInlineBtn = toolbar.container.querySelector(".ql-smartInline");

        expect(smartTagBtn).toBeDefined();
        expect(smartInlineBtn).toBeDefined();

        // Test setting content with smart tags
        quill.clipboard.dangerouslyPasteHTML(
            '<p>Test with <span class="smart-tag" data-type="study" data-pk="1">smart tag</span></p>'
        );

        const content = quill.getSemanticHTML();
        expect(content).toContain("smart-tag");
        expect(content).toContain("data-type");
        expect(content).toContain("data-pk");

        // Clean up
        document.body.removeChild(editorDiv);
    });
});
