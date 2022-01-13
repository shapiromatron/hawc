import {addOuterTag} from "shared/utils/_helpers";
import assert from "../../helpers";

describe("shared/utils/helpers", function() {
    describe("addOuterTag", function() {
        it("adds tags when needed", function() {
            assert.equal(addOuterTag("", "p"), "<p></p>");
            assert.equal(addOuterTag("hi", "p"), "<p>hi</p>");
            assert.equal(addOuterTag("<li>hi</li>", "p"), "<p><li>hi</li></p>");
            assert.equal(addOuterTag("a<span>hi</span>b", "p"), "<p>a<span>hi</span>b</p>");
            // TODO - fails when tag has an attribute
            assert.equal(addOuterTag('<p class="foo">hi</p>', "p"), '<p><p class="foo">hi</p></p>');
        });
        it("doesn't add tags when not needed", function() {
            assert.equal(addOuterTag("<p></p>", "p"), "<p></p>");
            assert.equal(addOuterTag("<p>hi</p>", "p"), "<p>hi</p>");
        });
    });
});
