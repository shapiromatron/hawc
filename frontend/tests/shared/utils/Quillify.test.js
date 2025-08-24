import {beforeEach, describe, expect, it, vi} from "vitest";

// Mock DOM environment for tests
Object.defineProperty(window, "alert", {
    value: vi.fn(),
});

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
    it("should register SmartTag and SmartInline blots correctly", async () => {
        const SmartTag = (await import("shared/smartTags/QuillSmartTag")).default;
        const SmartInline = (await import("shared/smartTags/QuillSmartInline")).default;

        // Verify blots are properly configured
        expect(SmartTag.blotName).toBe("smartTag");
        expect(SmartTag.tagName).toBe("SPAN");
        expect(SmartInline.blotName).toBe("smartInline");
        expect(SmartInline.tagName).toBe("DIV");

        // Verify blots can create elements correctly
        const smartTagEl = SmartTag.create({pk: 1, type: "study"});
        expect(smartTagEl.tagName).toBe("SPAN");
        expect(smartTagEl.dataset.pk).toBe("1");
        expect(smartTagEl.dataset.type).toBe("study");
        expect(smartTagEl.className).toContain("smart-tag");

        const smartInlineEl = SmartInline.create({pk: 2, type: "endpoint"});
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

    it("should create basic Quill instance with updated API", async () => {
        const Quill = (await import("quill")).default;

        // Create a simple div for the editor
        const editorDiv = document.createElement("div");
        document.body.appendChild(editorDiv);

        // Create Quill instance with basic configuration
        const quill = new Quill(editorDiv, {
            theme: "snow",
            modules: {
                toolbar: [["bold", "italic"], ["clean"]],
            },
        });

        // Test that Quill 2.x API methods are available
        expect(typeof quill.clipboard.dangerouslyPasteHTML).toBe("function");
        expect(typeof quill.getSemanticHTML).toBe("function");

        // Test setting content using new API
        quill.clipboard.dangerouslyPasteHTML("<p>Test content</p>");

        // Test getting content using new API
        const content = quill.getSemanticHTML();
        expect(content).toContain("Test");
        expect(content).toContain("content");

        // Clean up
        document.body.removeChild(editorDiv);
    });

    it("should work with Quill 2.x text-change events", async () => {
        const Quill = (await import("quill")).default;

        // Create a simple div for the editor
        const editorDiv = document.createElement("div");
        document.body.appendChild(editorDiv);

        const quill = new Quill(editorDiv, {
            theme: "snow",
        });

        // Test text-change event handler
        let lastChange = null;
        quill.on("text-change", (delta, oldDelta, source) => {
            lastChange = {delta, oldDelta, source};
        });

        // Insert text
        quill.insertText(0, "Hello world");

        // Wait for event to process
        await new Promise(resolve => setTimeout(resolve, 10));

        expect(lastChange).not.toBe(null);
        expect(lastChange.source).toBe("api");

        // Test getting the content
        const content = quill.getSemanticHTML();
        expect(content).toContain("Hello");
        expect(content).toContain("world");

        // Clean up
        document.body.removeChild(editorDiv);
    });

    it("should create Quill instance with custom toolbar including smart tag buttons", async () => {
        const Quill = (await import("quill")).default;

        // Register the blots first
        const SmartTag = (await import("shared/smartTags/QuillSmartTag")).default;
        const SmartInline = (await import("shared/smartTags/QuillSmartInline")).default;

        Quill.register(SmartTag, true);
        Quill.register(SmartInline, true);

        const editorDiv = document.createElement("div");
        document.body.appendChild(editorDiv);

        const toolbarOptions = {
            container: [
                [{header: [false, 1, 2, 3, 4]}],
                ["bold", "italic", "underline", "strike"],
                [{script: "sub"}, {script: "super"}],
                [{color: []}, {background: []}],
                ["link", {list: "ordered"}, {list: "bullet"}, "blockquote"],
                ["smartTag", "smartInline"],
                ["clean"],
            ],
            handlers: {
                smartTag(_value) {
                    let sel = this.quill.getSelection();
                    if (sel === null || sel.length === 0) {
                        return false;
                    }
                    return true;
                },
                smartInline(_value) {
                    let sel = this.quill.getSelection();
                    if (sel === null || sel.length === 0) {
                        return false;
                    }
                    return true;
                },
            },
        };

        const quill = new Quill(editorDiv, {
            modules: {
                toolbar: toolbarOptions,
            },
            theme: "snow",
        });

        // Check that toolbar module exists
        const toolbar = quill.getModule("toolbar");
        expect(toolbar).toBeDefined();
        expect(toolbar.container).toBeDefined();

        // Check that smart tag buttons were created
        const smartTagBtn = toolbar.container.querySelector(".ql-smartTag");
        const smartInlineBtn = toolbar.container.querySelector(".ql-smartInline");

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
