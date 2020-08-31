import * as d3 from "d3";
import $ from "$";
import React from "react";
import _ from "lodash";
import moment from "moment";

const stopwords = new Set("the is at which of on".split(" "));
const helpers = {
    noop() {},
    fetchGet: {
        credentials: "same-origin",
    },
    fetchPost(csrf, obj, verb = "POST") {
        obj["csrfmiddlewaretoken"] = csrf;
        return {
            credentials: "same-origin",
            method: verb,
            headers: new Headers({
                "X-CSRFToken": csrf,
                "content-type": "application/json",
            }),
            body: JSON.stringify(obj),
        };
    },
    fetchForm(csrf, form, verb = "POST") {
        // form should be a <form> html element
        return {
            credentials: "same-origin",
            method: verb,
            headers: new Headers({
                "X-CSRFToken": csrf,
                "content-type": "application/x-www-form-urlencoded",
            }),
            body: $(form).serialize(),
        };
    },
    fetchBulk(csrf, obj, verb = "PATCH") {
        obj["csrfmiddlewaretoken"] = csrf;
        return {
            credentials: "same-origin",
            method: verb,
            headers: new Headers({
                "X-CSRFToken": csrf,
                "content-type": "application/json",
                "X-CUSTOM-BULK-OPERATION": true,
            }),
            body: JSON.stringify(obj),
        };
    },
    fetchDelete(csrf) {
        return {
            credentials: "same-origin",
            method: "DELETE",
            headers: new Headers({
                "X-CSRFToken": csrf,
                "content-type": "application/json",
            }),
            body: JSON.stringify({csrfmiddlewaretoken: csrf}),
        };
    },
    goBack(e) {
        if (e && e.preventDefault) e.preventDefault();
        window.history.back();
    },
    getValue(target) {
        let val;
        switch (target.type) {
            case "checkbox":
                return target.checked;
            case "number":
                return parseFloat(target.value);
            case "select-one": // use isFinite in-case value is 0
                val = parseInt(target.value);
                return _.isFinite(val) ? val : target.value;
            case "text":
            case "textarea":
            default:
                return target.value;
        }
    },
    getObjectUrl(host, base, id) {
        return `${host}${base}${id}/`;
    },
    getListUrl(host, base) {
        return `${host}${base}`;
    },
    getUrlWithAssessment(url, assessment_id) {
        return `${url}?assessment_id=${assessment_id}`;
    },
    getBulkUrl(host, base, ids = null) {
        return `${host}${base}&ids=${ids}`;
    },
    datetimeFormat(dt) {
        return moment(dt).format("MMMM Do YYYY, h:mm:ss a");
    },
    booleanCheckbox(val) {
        if (val) {
            return <i className="fa fa-check-square-o" title="checked" />;
        } else {
            return <i className="fa fa-square-o" title="un-checked" />;
        }
    },
    getInputDivClass(name, errors, extra = []) {
        extra.push("form-group");
        if (errors && errors[name]) extra.push("has-error");
        return extra.join(" ");
    },
    deepCopy(object) {
        return JSON.parse(JSON.stringify(object));
    },
    caseToWords(string) {
        return (
            string
                // replace underscores and dashes with spaces
                .replace(/[_-]/g, " ")
                // insert a space between lower followed by upper
                .replace(/([a-z])([A-Z])/g, "$1 $2")
                // insert a space between last upper in sequence followed by lower
                .replace(/\b([A-Z]+)([A-Z])([a-z])/, "$1 $2$3")
                // uppercase the first character of first word
                .replace(/\w\S*/, function(txt) {
                    return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
                })
        );
    },
    titleCase(string) {
        // convert lower case "reference id " -> "Reference ID"
        // special case acronyms include:
        // ID, HAWC, HERO, NOEL (and NEL/NOAEL, FEL, LEL variants) and BMD (BMDL/U)
        return string
            .toLowerCase()
            .replace(/[_-]/g, " ")
            .replace(/\b\w+/g, match => {
                return stopwords.has(match)
                    ? match
                    : match.charAt(0).toUpperCase() + match.substr(1).toLowerCase();
            })
            .replace(/\b(?:id|hawc|hero|[nfl]o?a?el|bmd[lu]?)\b/gi, match => match.toUpperCase());
    },
    hideRobScore(assessment_id) {
        // TODO - remove 100500031 hack
        return assessment_id === 100500031;
    },
    getHawcContentSize() {
        // for the standard hawc page layout, get the width and height for the main `content` box
        const contentSize = document.getElementById("content").getBoundingClientRect(),
            windowHeight = window.innerHeight;
        return {
            width: contentSize.width,
            height: windowHeight - contentSize.top,
        };
    },
    getTextContrastColor(hex) {
        /* Returns white or black based on best contrast for given background color
           Based on W3C guidelines: https://www.w3.org/TR/UNDERSTANDING-WCAG20/visual-audio-contrast-contrast.html
         */
        let {r, b, g} = d3.rgb(hex);
        if (r > 255 || r < 0) throw `RGB values must be between 0 and 255. R value was ${r}.`;
        if (g > 255 || g < 0) throw `RGB values must be between 0 and 255. G value was ${g}.`;
        if (b > 255 || b < 0) throw `RGB values must be between 0 and 255. B value was ${b}.`;
        (r /= 255), (g /= 255), (b /= 255);
        let r_component = r <= 0.03928 ? r / 12.92 : ((r + 0.055) / 1.055) ** 2.4,
            g_component = g <= 0.03928 ? g / 12.92 : ((g + 0.055) / 1.055) ** 2.4,
            b_component = b <= 0.03928 ? b / 12.92 : ((b + 0.055) / 1.055) ** 2.4,
            luminance = 0.2126 * r_component + 0.7152 * g_component + 0.0722 * b_component;
        return luminance > Math.sqrt(1.05 * 0.05) - 0.05 ? "#000000" : "#ffffff";
    },
    randomString() {
        return "xxxxxxxxxxxxxxx".replace(/x/g, c =>
            String.fromCharCode(97 + parseInt(26 * Math.random()))
        );
    },
    hashString(string) {
        let hash = 0,
            i,
            chr;
        for (i = 0; i < string.length; i++) {
            chr = string.charCodeAt(i);
            hash = (hash << 5) - hash + chr;
            hash |= 0; // Convert to 32bit integer
        }
        return `hash-${hash}`;
    },
    setIntersection(set1, set2) {
        return new Set([...set1].filter(x => set2.has(x)));
    },
    setDifference(arr, removeSet) {
        // https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Set
        let _difference = new Set(arr);
        for (let elem of removeSet) {
            _difference.delete(elem);
        }
        return [..._difference];
    },
    cartesian(arrs) {
        // arrs is an array of arrays
        // https://stackoverflow.com/a/43053803/906385
        const f = (a, b) => [].concat(...a.map(d => b.map(e => [].concat(d, e))));
        const _cartesian = (a, b, ...c) => (b ? _cartesian(f(a, b), ...c) : a);
        return _cartesian(...arrs);
    },
    COLORS: {
        WHITE: "#ffffff",
        BLUE: "#003d7b",
    },
};

export default helpers;
