import assert from "assert";
import Format from "shared/parsers/format";

const obj = {one: 1, two: "two"},
    getValue = prop => obj[prop],
    options = {getValue};

describe("shared/parsers/format", function() {
    describe("Format", function() {
        it("handles a substitute", function() {
            let actual = Format.parse("${one}", options),
                expected = "1";
            assert.ok(actual == expected);
        });
        it("handles multiple substitutes", function() {
            let actual = Format.parse("${one} and ${two}", options),
                expected = "1 and two";
            assert.ok(actual == expected);
        });
        it("handles no substitutes", function() {
            let actual = Format.parse("No numbers!", options),
                expected = "No numbers!";
            assert.ok(actual == expected);
        });
        it("handles leading and trailing literals", function() {
            let actual = Format.parse("1 + ${one} = 2", options),
                expected = "1 + 1 = 2";
            assert.ok(actual == expected);
        });
        it("handles leading and trailing literals", function() {
            let actual = Format.parse("1 + ${one} = 2", options),
                expected = "1 + 1 = 2";
            assert.ok(actual == expected);
        });
        it("handles escaped characters", function() {
            let actual = Format.parse("\\${one}", options),
                expected = "${one}";
            assert.ok(actual == expected);
        });
        it("handles ternary true", function() {
            let actual = Format.parse("match(one,1)?This is true:This is false", options),
                expected = "This is true";
            assert.ok(actual == expected);
        });
        it("handles ternary false", function() {
            let actual = Format.parse("match(one,2)?This is true:This is false", options),
                expected = "This is false";
            assert.ok(actual == expected);
        });
        it("handles ternary integer match", function() {
            let actual = Format.parse("match(one,1)?This is true:This is false", options),
                expected = "This is true";
            assert.ok(actual == expected);
        });
        it("handles ternary string match", function() {
            let actual = Format.parse('match(two,"two")?This is true:This is false', options),
                expected = "This is true";
            assert.ok(actual == expected);
        });
        it("unable to parse bad strings", function() {
            // substitutions need to be closed
            assert.throws(() => Format.parse("${identifier", options));
        });
    });
});
