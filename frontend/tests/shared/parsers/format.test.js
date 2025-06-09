import assert from "assert";
import {parse} from "shared/parsers/format";

const obj = {one: 1, two: "two", three: "", four: null, float: 123.123456},
    getValue = prop => obj[prop],
    options = {getValue};

describe("shared/parsers/format", function () {
    describe("Format", function () {
        it("handles a substitute", function () {
            let actual = parse("${one}", options),
                expected = "1";
            assert.ok(actual == expected);
        });
        it("handles multiple substitutes", function () {
            let actual = parse("${one} and ${two}", options),
                expected = "1 and two";
            assert.ok(actual == expected);
        });
        it("handles no substitutes", function () {
            let actual = parse("No numbers!", options),
                expected = "No numbers!";
            assert.ok(actual == expected);
        });
        it("handles leading and trailing literals", function () {
            let actual = parse("1 + ${one} = 2", options),
                expected = "1 + 1 = 2";
            assert.ok(actual == expected);
        });
        it("handles leading and trailing literals", function () {
            let actual = parse("1 + ${one} = 2", options),
                expected = "1 + 1 = 2";
            assert.ok(actual == expected);
        });
        it("handles escaped characters", function () {
            let actual = parse("\\${one}", options),
                expected = "${one}";
            assert.ok(actual == expected);
        });
        it("handles ternary true", function () {
            let actual = parse("match(one,1)?This is true:This is false", options),
                expected = "This is true";
            assert.ok(actual == expected);
        });
        it("handles ternary false", function () {
            let actual = parse("match(one,2)?This is true:This is false", options),
                expected = "This is false";
            assert.ok(actual == expected);
        });
        it("handles ternary integer match", function () {
            let actual = parse("match(one,1)?This is true:This is false", options),
                expected = "This is true";
            assert.ok(actual == expected);
        });
        it("handles ternary string match", function () {
            let actual = parse('match(two,"two")?This is true:This is false', options),
                expected = "This is true";
            assert.ok(actual == expected);
        });
        it("handles ternary exists for existing value", function () {
            let actual = parse("exists(one)?This is true:This is false", options),
                expected = "This is true";
            assert.ok(actual == expected);
        });
        it("handles ternary exists for empty string", function () {
            let actual = parse("exists(three)?This is true:This is false", options),
                expected = "This is false";
            assert.ok(actual == expected);
        });
        it("handles ternary exists for null value", function () {
            let actual = parse("exists(four)?This is true:This is false", options),
                expected = "This is false";
            assert.ok(actual == expected);
        });
        it("handles good round", function () {
            assert.ok(parse("round(float,0)", options) == "123");
            assert.ok(parse("round(float,1)", options) == "123.1");
            assert.ok(parse("round(float,2)", options) == "123.12");
            assert.ok(parse("***round(float,2)***", options) == "***123.12***");
        });
        it("handles bad round", function () {
            assert.ok(parse("round(two,0)", options) == "");
        });
        it("handles complex ternary", function () {
            let actual = parse(
                    'match(one,1)?match(two,"two")?${one}=1 and ${two}=two:${two}!=two:${one}!=1',
                    options
                ),
                expected = "1=1 and two=two";
            assert.ok(actual == expected);
        });
        it("unable to parse bad strings", function () {
            // substitutions need to be closed
            assert.throws(() => parse("${identifier", options));
        });
    });
});
