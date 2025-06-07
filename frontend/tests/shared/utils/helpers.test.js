import {addOuterTag, escapeRegex, markKeywords} from "shared/utils/_helpers";

import assert from "../../helpers";

describe("shared/utils/helpers", function () {
    describe("addOuterTag", function () {
        it("adds tags when needed", function () {
            assert.equal(addOuterTag("", "p"), "<p></p>");
            assert.equal(addOuterTag("hi", "p"), "<p>hi</p>");
            assert.equal(addOuterTag("<li>hi</li>", "p"), "<p><li>hi</li></p>");
            assert.equal(addOuterTag("a<span>hi</span>b", "p"), "<p>a<span>hi</span>b</p>");
            // TODO - fails when tag has an attribute
            assert.equal(addOuterTag('<p class="foo">hi</p>', "p"), '<p><p class="foo">hi</p></p>');
        });
        it("doesn't add tags when not needed", function () {
            assert.equal(addOuterTag("<p></p>", "p"), "<p></p>");
            assert.equal(addOuterTag("<p>hi</p>", "p"), "<p>hi</p>");
        });
    });
    describe("markKeywords", function () {
        it("highlights matching text from a keyword list", function () {
            const settings = {
                set1: {
                    name: "Positive",
                    color: "#228833",
                    keywords: ["burrito", "chil*"],
                },
                set2: {
                    name: "Negative",
                    color: "#ee6677",
                    keywords: ["ea*", "*bat*"],
                },
                set3: {
                    name: "Additional",
                    color: "#4477aa",
                    keywords: [],
                },
            };
            assert.equal(
                markKeywords("burrito", settings),
                '<mark class="hawc-mk" title="Positive" style="border-bottom: 1px solid #228833; box-shadow: inset 0 -4px 0 #228833;">burrito</mark>'
            );
            assert.equal(markKeywords("burritos", settings), "burritos");
            assert.equal(markKeywords("burito", settings), "burito");
            assert.equal(
                markKeywords("chil", settings),
                '<mark class="hawc-mk" title="Positive" style="border-bottom: 1px solid #228833; box-shadow: inset 0 -4px 0 #228833;">chil</mark>'
            );
            assert.equal(
                markKeywords("child", settings),
                '<mark class="hawc-mk" title="Positive" style="border-bottom: 1px solid #228833; box-shadow: inset 0 -4px 0 #228833;">child</mark>'
            );
            assert.equal(
                markKeywords("of each one", settings),
                'of <mark class="hawc-mk" title="Negative" style="border-bottom: 1px solid #ee6677; box-shadow: inset 0 -4px 0 #ee6677;">each</mark> one'
            );
            assert.equal(
                markKeywords("wow thebatman is here", settings),
                'wow <mark class="hawc-mk" title="Negative" style="border-bottom: 1px solid #ee6677; box-shadow: inset 0 -4px 0 #ee6677;">thebatman</mark> is here'
            );
        });
    });
    describe("escapeRegex", function () {
        it("escapes special regex characters from text", function () {
            const regText =
                "phenylbenzene-1,4-diamine|6-PPDQ|2-anilino-5-[(4-methylpentan-2-yl)amino]cyclohexa-2,5-diene-1,4-dione";
            assert.equal(
                escapeRegex(regText),
                "phenylbenzene-1,4-diamine\\|6-PPDQ\\|2-anilino-5-\\[\\(4-methylpentan-2-yl\\)amino\\]cyclohexa-2,5-diene-1,4-dione"
            );
        });
        it("doesn't escape text without any special characters", function () {
            assert.equal(
                escapeRegex("no special characters to escape"),
                "no special characters to escape"
            );
        });
    });
});
