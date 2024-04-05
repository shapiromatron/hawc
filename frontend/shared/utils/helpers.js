import * as d3 from "d3";
import _ from "lodash";
import moment from "moment";
import React from "react";
import ReactDOM from "react-dom";

import $ from "$";

import {addOuterTag} from "./_helpers";

const stopwords = new Set("the is at which of on".split(" ")),
    hexChars = "abcdef0123456789",
    regexEscapeChars = /[-|\\{}()[\]^$+*?.]/g,
    excelColumn = column => String.fromCharCode(65 + column),
    hexToRgb = hex => {
        // http://stackoverflow.com/questions/5623838/
        hex = hex.replace(/^#?([a-f\d])([a-f\d])([a-f\d])$/i, function(m, r, g, b) {
            return r + r + g + g + b + b;
        });

        var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
        return result
            ? {
                  r: parseInt(result[1], 16),
                  g: parseInt(result[2], 16),
                  b: parseInt(result[3], 16),
              }
            : null;
    };

const helpers = {
    noop() {},
    fetchGet: {
        credentials: "same-origin",
    },
    docUrlRoot: "https://hawc.readthedocs.io",
    escapeRegexString(unescapedString) {
        // https://www.npmjs.com/package/escape-regex-string
        return unescapedString.replace(regexEscapeChars, "\\$&");
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
    fetchPostFile(csrf, file) {
        return {
            credentials: "same-origin",
            method: "POST",
            headers: {
                "X-CSRFToken": csrf,
                "Content-Disposition": "attachment; filename=upload.xlsx",
            },
            body: file,
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
    handleSubmit(url, verb, csrf, obj, success, failure, error) {
        const payload = this.fetchPost(csrf, obj, verb);
        fetch(url, payload)
            .then(response => {
                if (response.ok) {
                    response.json().then(response => success(response));
                } else {
                    response.json().then(response => failure(response));
                }
            })
            .catch(exception => {
                if (error) {
                    console.error("Submission failed", exception);
                } else {
                    error(exception);
                }
            });
    },
    ff(number) {
        // ff = float format
        if (number === 0) {
            return number.toString();
        } else if (number === -9999) {
            return "-";
        } else if (Math.abs(number) > 0.001 && Math.abs(number) < 1e9) {
            // local print "0" for anything smaller than this
            return number.toLocaleString();
        } else {
            // too many 0; use exponential notation
            return number.toExponential(2);
        }
    },
    dateToString(date) {
        var pad = x => (x < 10 ? "0" : "") + x;
        if (date.getTime()) {
            var d = pad(date.getDate()),
                m = pad(date.getMonth() + 1),
                y = date.getFullYear(),
                hr = pad(date.getHours()),
                min = pad(date.getMinutes());
            return [y, m, d].join("/") + " " + hr + ":" + min;
        }
        return "";
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
    getUrlWithParameters(path, params) {
        return `${path}?${new URLSearchParams(params).toString()}`;
    },
    datetimeFormat(dt) {
        return moment(dt).format("MMMM Do YYYY, h:mm:ss a");
    },
    booleanCheckbox(val) {
        if (val) {
            return <i className="fa fa-check-square-o" title="true" />;
        } else {
            return <i className="fa fa-times-rectangle-o" title="false" />;
        }
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
    pluralize(word, length) {
        // word: str
        // items: int
        return `${length} ${word}${length === 1 ? "" : "s"}`;
    },
    titleCase(string) {
        // convert lower case "reference id " -> "Reference ID"
        // special case acronyms include:
        // ID, HAWC, HERO, URL, NOEL (and NEL/NOAEL, FEL, LEL variants), and BMD (BMDL/U)
        return string
            .toLowerCase()
            .replace(/[_-]/g, " ")
            .replace(/\b\w+/g, match => {
                return stopwords.has(match)
                    ? match
                    : match.charAt(0).toUpperCase() + match.substr(1).toLowerCase();
            })
            .replace(/\b(?:id|hawc|hero|url|[nfl]o?a?el|bmd[lu]?)\b/gi, match =>
                match.toUpperCase()
            );
    },
    getHawcContentSize() {
        // for the standard hawc page layout, get the width and height for the main `content` box
        const contentSize = document
                .getElementById("main-content-container")
                .getBoundingClientRect(),
            windowHeight = window.innerHeight;
        return {
            width: contentSize.width,
            height: windowHeight - contentSize.top,
        };
    },
    getAbsoluteOffsets(el) {
        // get offsets of element relative to document body
        let bodyRect = document.body.getBoundingClientRect(),
            elRect = el.getBoundingClientRect();
        return {
            left: elRect.left - bodyRect.left,
            top: elRect.top - bodyRect.top,
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
    randomString(length = 15) {
        return Array(length)
            .fill()
            .map(() => hexChars.charAt(Math.floor(Math.random() * hexChars.length)))
            .join("");
    },
    renameProperty(obj, oldName, newName) {
        obj[newName] = obj[oldName];
        delete obj[oldName];
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
    numLogTicks(domain) {
        // number of ticks to be used for a given dataset.
        // domain should be output of d3.extent, eg., [1, 100]
        return Math.max(
            2,
            Math.min(Math.ceil(Math.log10(domain[1])) - Math.floor(Math.log10(domain[0])), 10)
        );
    },
    excelColumn,
    excelCoords(row, column) {
        // column and row are 0-based
        return `${excelColumn(column)}${row + 1}`;
    },
    addOuterTag,
    hasInnerText(text) {
        // wrap text with html tag to ensure it is a valid jQuery selector expression
        // then return whether there is text content
        return (
            $(`<div>${text}</div>`)
                .text()
                .trim().length > 0
        );
    },
    numericAxisFormat: d3.format(",~g"),
    contrastingColor(hex) {
        // http://stackoverflow.com/questions/1855884/
        var rgb = hexToRgb(hex),
            a = 1 - (0.299 * rgb.r + 0.587 * rgb.g + 0.114 * rgb.b) / 255;
        return a < 0.5 ? "#404040" : "#ffffff";
    },
    COLORS: {
        WHITE: "#ffffff",
        BLUE: "#003d7b",
    },
    pushUrlParamsState(key, value) {
        var queryParams = new URLSearchParams(window.location.search);
        if (_.isNil(value)) {
            queryParams.delete(key);
        } else {
            queryParams.set(key, value);
        }
        history.pushState(null, null, "?" + queryParams.toString());
    },
    nullString: "<null>",
    maybeScrollIntoView(reactNode, options) {
        // scroll into view if not currently visible; can optionally specify an offset too.
        // eslint-disable-next-line react/no-find-dom-node
        const node = ReactDOM.findDOMNode(reactNode);
        options = options || {};
        if (node) {
            setTimeout(() => {
                const rect = node.getBoundingClientRect(),
                    isVisible = rect.top >= 0 && rect.bottom <= window.innerHeight,
                    y = rect.top + window.pageYOffset + (options.yOffset || 0);
                if (!isVisible) {
                    window.scrollTo({top: y, behavior: "smooth"});
                    if (options.animate) {
                        node.animate(
                            [
                                {transform: "translateY(-2px)"},
                                {transform: "translateY(4px)"},
                                {transform: "translateY(-2px)"},
                            ],
                            {delay: 1000, duration: 100, iterations: 3}
                        );
                    }
                }
            }, 250);
        }
    },
    groupNest(values, ...keys) {
        // performs d3.group and transforms it into the old d3.nest structure
        function groupToNest(group, depth) {
            if (depth-- > 0) {
                return Array.from(group, ([_key, _values]) => ({
                    key: _key,
                    values: groupToNest(_values, depth),
                }));
            }
            return group;
        }
        let group = d3.group(values, ...keys),
            depth = keys.length;
        return groupToNest(group, depth);
    },
    castNumberOrKeepString: text => {
        const maybeNumber = parseFloat(text);
        return isNaN(maybeNumber) ? text : maybeNumber;
    },
};
export default helpers;
