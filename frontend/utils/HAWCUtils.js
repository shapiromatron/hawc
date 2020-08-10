import $ from "$";
import _ from "lodash";
import * as d3 from "d3";
import slugify from "slugify";

import renderChemicalDetails from "./components/ChemicalDetails";

class HAWCUtils {
    static HAWC_NEW_WINDOW_POPUP_CLOSING = "hawcNewWindowPopupClosing";

    static booleanCheckbox(value) {
        return value
            ? `<i class="fa fa-check"><span class="invisible">${value}</span></i>`
            : `<i class="fa fa-minus"><span class="invisible">${value}</span></i>`;
    }

    static newWindowPopupLink(triggeringLink) {
        // Force new window to be a popup window
        var href = triggeringLink.href + "?_popup=1";
        var win = window.open(href, "_blank", "height=500,width=980,resizable=yes,scrollbars=yes");
        win.focus();

        win.onbeforeunload = function(e) {
            let event = new CustomEvent(window.app.utils.HAWCUtils.HAWC_NEW_WINDOW_POPUP_CLOSING, {
                detail: {},
            });
            triggeringLink.dispatchEvent(event);
            // interested listeners can access fields in detail e.g. "customField" via e.originalEvent.detail.customField
        };

        return false;
    }

    static build_breadcrumbs(arr) {
        // builds a string of breadcrumb hyperlinks for navigation
        var links = [];
        arr.forEach(function(v) {
            links.push(`<a target="_blank" href="${v.url}">${v.name}</a>`);
        });
        return links.join("<span> / </span>");
    }

    static InitialForm(config) {
        var selector_val = config.form.find("#id_selector_1"),
            submitter = config.form.find("#submit_form");

        submitter.on("click", function() {
            var val = parseInt(selector_val.val(), 10);
            if (val) {
                submitter.attr("href", `${config.base_url}?initial=${val}`);
                return true;
            }
            return false;
        });
    }

    static prettifyVariableName(str) {
        str = str.replace(/_/g, " ");
        return str.charAt(0).toUpperCase() + str.substr(1);
    }

    static truncateChars(txt, n) {
        n = n || 200;
        if (txt.length > n) return txt.slice(0, n) + "...";
        return txt;
    }

    static pageActionsButton(items) {
        var $menu = $('<ul class="dropdown-menu">');
        items.forEach(function(d) {
            if (d instanceof Object) {
                $menu.append(`<li><a href="${d.url}" class="${d.cls || ""}">${d.text}</a></li>`);
            } else if (typeof d === "string") {
                $menu.append(`<li class="disabled"><a tabindex="-1" href="#">${d}</a></li>`);
            } else {
                console.error("unknown input type");
            }
        });
        return $('<div class="btn-group pull-right">')
            .append(
                '<a class="btn btn-primary dropdown-toggle" data-toggle="dropdown">Actions <span class="caret"></span></a>'
            )
            .append($menu);
    }

    static addAlert(content, $div) {
        $div = $div || $("#content");
        $div.prepend(
            $('<div class="alert">')
                .append('<button type="button" class="close" data-dismiss="alert">&times;</button>')
                .append(content)
        );
    }

    static abstractMethod() {
        throw "Abstract method; requires implementation";
    }

    static renderChemicalProperties(url, $div, show_header) {
        const handleResponse = function(data) {
                if (data.status === "requesting") {
                    setTimeout(tryToFetch, 1000);
                }
                if (data.status === "success") {
                    renderChemicalDetails($div.get(0), data.content, show_header);
                }
            },
            tryToFetch = () => {
                fetch(url)
                    .then(resp => resp.json())
                    .then(handleResponse);
            };

        tryToFetch();
    }

    static updateDragLocationTransform(setDragCB) {
        // a new drag location, requires binding to d3.drag,
        // and requires a _.partial injection of th settings module.
        const re_floats = /(-?[0-9]*\.?[0-9]+)/gm,
            getFloats = function(txt) {
                // expects an attribute like 'translate(277', '1.1920928955078125e-7)'
                if (_.isNull(txt) || txt.indexOf("translate") !== 0) return;
                return [...txt.matchAll(re_floats)].map(d => parseFloat(d[0]));
            };

        return d3.drag().on("drag", function() {
            var x,
                y,
                p = d3.select(this),
                text = p.attr("transform"),
                coords = getFloats(text);

            if (coords && coords.length >= 2) {
                if (coords.length === 2) {
                    // no rotation
                    x = parseInt(coords[0] + d3.event.dx);
                    y = parseInt(coords[1] + d3.event.dy);
                    p.attr("transform", `translate(${x},${y})`);
                    if (setDragCB) {
                        setDragCB.bind(this)(x, y);
                    }
                } else if (coords.length === 3) {
                    // has rotation
                    x = parseInt(coords[0] + d3.event.dx);
                    y = parseInt(coords[1] + d3.event.dy);
                    p.attr("transform", `translate(${x},${y}) rotate(${coords[2]})`);
                    if (setDragCB) {
                        setDragCB.bind(this)(x, y);
                    }
                } else {
                    console.error(`Unknown parsing of string ${text}`);
                }
            }
        });
    }

    static updateDragLocationXY(setDragCB) {
        // a new drag location, requires binding to d3.drag,
        // and requires a _.partial injection of th settings module.
        return d3.drag().on("drag", function() {
            var p = d3.select(this),
                x = parseInt(parseInt(p.attr("x"), 10) + d3.event.dx, 10),
                y = parseInt(parseInt(p.attr("y"), 10) + d3.event.dy, 10);

            p.attr("x", x);
            p.attr("y", y);
            if (setDragCB) {
                setDragCB.bind(this)(x, y);
            }
        });
    }

    static wrapText(text, max_width) {
        if (!$.isNumeric(max_width) || max_width <= 0) return;
        var $text = d3.select(text),
            words = text.textContent.split(/\s+/).reverse(),
            word,
            line = [],
            lineNumber = 0,
            lineHeight = text.getBBox().height, // px
            x = $text.attr("x"),
            y = $text.attr("y"),
            tspan = $text
                .text(null)
                .append("tspan")
                .attr("x", x)
                .attr("y", y);

        while ((word = words.pop())) {
            line.push(word);
            tspan.text(line.join(" "));
            if (tspan.node().getComputedTextLength() > max_width && line.length > 1) {
                line.pop();
                tspan.text(line.join(" "));
                line = [word];
                tspan = $text
                    .append("tspan")
                    .attr("x", x)
                    .attr("y", y)
                    .attr("dy", ++lineNumber * lineHeight + "px")
                    .text(word);
            }
        }
    }

    static isSupportedBrowser() {
        // not ideal; but <IE12 isn't supported which is primary-goal:
        // http://webaim.org/blog/user-agent-string-history/
        var ua = navigator.userAgent.toLowerCase(),
            isChrome = ua.indexOf("chrome") > -1,
            isFirefox = ua.indexOf("firefox") > -1,
            isSafari = ua.indexOf("safari") > -1;
        return isChrome || isFirefox || isSafari;
    }

    static browserCheck() {
        if (!HAWCUtils.isSupportedBrowser()) {
            $("#content").prepend(
                $('<div class="alert">')
                    .append(
                        '<button id="hideBrowserWarning" type="button" class="close" data-dismiss="alert">&times;</button>'
                    )
                    .append(
                        '<b>Warning:</b> Your current browser has not been tested extensively with this website, which may result in some some errors with functionality. The following browsers are fully supported:<ul><li><a href="https://www.google.com/chrome/" target="_blank">Google Chrome</a> (preferred)</li><li><a href="https://www.mozilla.org/firefox/" target="_blank">Mozilla Firefox</a></li><li><a href="https://www.apple.com/safari/" target="_blank">Apple Safari</a></li></ul>Please use a different browser for an optimal experience.'
                    )
            );
        }
    }

    static buildUL(lst, func) {
        const items = _.map(lst, func).join("");
        return `<ul>${items}</ul>`;
    }

    static isHTML(str) {
        var a = document.createElement("div");
        a.innerHTML = str;
        for (var c = a.childNodes, i = c.length; i--; ) {
            if (c[i].nodeType == 1) return true;
        }
        return false;
    }

    static urlify(str) {
        return slugify(str);
    }

    static parseJsonOrNull(el) {
        // return a JSON version or the object OR null
        // based on https://stackoverflow.com/a/20392392
        if (
            el !== null &&
            typeof el == "string" &&
            el.charAt(0) == "{" &&
            el.charAt(el.length - 1) == "}"
        ) {
            try {
                let o = JSON.parse(el);
                if (o && typeof o === "object") {
                    return o;
                }
            } catch (e) {
                console.warn("un-parsable JSON-like string", el);
            }
        }
        return null;
    }

    static printf(str) {
        // https://stackoverflow.com/a/4673436/906385
        const args = Array.prototype.slice.call(arguments, 1);
        return str.replace(/{(\d+)}/g, (match, number) =>
            typeof args[number] !== "undefined" ? args[number] : match
        );
    }

    static symbolStringToType(str) {
        switch (str) {
            case "circle":
                return d3.symbolCircle;
            case "cross":
                return d3.symbolCross;
            case "diamond":
                return d3.symbolDiamond;
            case "square":
                return d3.symbolSquare;
            case "star":
                return d3.symbolStar;
            case "triangle":
            case "triangle-up":
                return d3.symbolTriangle;
            case "triangle-down":
                return {
                    draw(context, size) {
                        var sqrt3 = Math.sqrt(3),
                            y = -Math.sqrt(size / (sqrt3 * 3));
                        context.moveTo(0, -y);
                        context.lineTo(-sqrt3 * y, y * 2);
                        context.lineTo(sqrt3 * y, y * 2);
                        context.closePath();
                    },
                };
            case "wye":
                return d3.symbolWye;
            default:
                console.error(`Unrecognized filter: ${str}`);
        }
    }
}

export default HAWCUtils;
