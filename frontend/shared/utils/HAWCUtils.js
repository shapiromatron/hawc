import * as d3 from "d3";
import _ from "lodash";
import slugify from "slugify";
import Tablesort from "tablesort";

import $ from "$";

import h from "./helpers";
import Hero from "./Hero";

class HAWCUtils {
    static Hero = Hero;
    static HAWC_NEW_WINDOW_POPUP_CLOSING = "hawcNewWindowPopupClosing";

    static booleanCheckbox(value) {
        return value
            ? `<i class="fa fa-check"><span class="invisible">${value}</span></i>`
            : `<i class="fa fa-times"><span class="invisible">${value}</span></i>`;
    }

    static newWindowPopupLink(triggeringLink) {
        // Force new window to be a popup window
        var href = triggeringLink.href + "?_popup=1";
        var win = window.open(href, "_blank", "height=500,width=980,resizable=yes,scrollbars=yes");
        win.focus();

        win.onbeforeunload = function(e) {
            let event = new CustomEvent(window.app.HAWCUtils.HAWC_NEW_WINDOW_POPUP_CLOSING, {
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
        var $menu = $(
            '<div class="dropdown-menu dropdown-menu-right" aria-labelledby="actionsDropdownButton">'
        );
        items.forEach(function(d) {
            if (d instanceof Object) {
                let attrs = _.map(d, (v, k) => (k == "text" ? "" : `${k}=${v}`)).join(" ");
                $menu.append(`<a class="dropdown-item" ${attrs}>${d.text}</a>`);
            } else if (typeof d === "string") {
                $menu.append(`<span class="dropdown-header">${d}</span>`);
            } else {
                console.error("unknown input type");
            }
        });
        return $(
            `<div class="actionsMenu dropdown btn-group ml-auto align-self-start flex-shrink-0 pl-2">`
        )
            .append(
                '<a class="btn btn-primary dropdown-toggle" id="actionsDropdownButton" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Actions</a>'
            )
            .append($menu);
    }

    static addAlert(content, $div) {
        $div = $div || $("#main-content-container");
        $div.prepend(
            $('<div class="alert alert-danger" data-testid="error">')
                .append('<button type="button" class="close" data-dismiss="alert">&times;</button>')
                .append("<i class='fa fa-fw fa-exclamation-triangle mr-1'></i>")
                .append(content)
        );
    }

    static abstractMethod() {
        throw "Abstract method; requires implementation";
    }

    static updateDragLocationTransform(setDragCB, options) {
        // a new drag location, requires binding to d3.drag,
        // and requires a _.partial injection of th settings module.
        const opts = options || {},
            re_floats = /(-?[0-9]*\.?[0-9]+)/gm,
            getFloats = function(txt) {
                // expects an attribute like 'translate(277', '1.1920928955078125e-7)'
                if (_.isNull(txt) || txt.indexOf("translate") !== 0) return;
                return [...txt.matchAll(re_floats)].map(d => parseFloat(d[0]));
            };

        return d3.drag().on("drag", function(event) {
            var x,
                y,
                p = d3.select(this),
                text = p.attr("transform"),
                coords = getFloats(text);

            if (opts.shift && !event.sourceEvent.shiftKey) {
                return;
            }

            if (coords && coords.length >= 2) {
                if (coords.length === 2) {
                    // no rotation
                    x = parseInt(coords[0] + event.dx);
                    y = parseInt(coords[1] + event.dy);
                    p.attr("transform", `translate(${x},${y})`);
                    if (setDragCB) {
                        setDragCB.bind(this)(x, y);
                    }
                } else if (coords.length === 3) {
                    // has rotation
                    x = parseInt(coords[0] + event.dx);
                    y = parseInt(coords[1] + event.dy);
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
        // and requires a _.partial injection of the settings module.
        return d3.drag().on("drag", function(event) {
            var p = d3.select(this),
                x = parseInt(parseInt(p.attr("x"), 10) + event.dx, 10),
                y = parseInt(parseInt(p.attr("y"), 10) + event.dy, 10);

            p.attr("x", x);
            p.attr("y", y);
            if (setDragCB) {
                setDragCB.bind(this)(x, y);
            }
        });
    }

    static wrapText(text, max_width) {
        if (!_.isFinite(max_width) || max_width <= 0) return;
        var $text = d3.select(text),
            // trim whitespace to prevent falsey empty strings after split
            words = text.textContent
                .trim()
                .split(/\s+/)
                .reverse(),
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

    static urlify(str, maxLength = 50, suffixLength = 4) {
        // transforms a given string into a url friendly slug
        // if the slug is greater than maxLength, then it is truncated and appended
        // with a random string (to ensure uniqueness if uniqueness is truncated)
        var slug = slugify(str, {remove: /[^\w\s-_]/g});
        return slug.length > maxLength
            ? slug.slice(0, maxLength - suffixLength - 1) + "-" + h.randomString(suffixLength)
            : slug;
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

    static loading() {
        return $(`<p class="loader">
            Loading, please wait...&nbsp;<span class="fa fa-spin fa-spinner"></span>
        </p>`);
    }

    static unpublished(published = true, editable = true) {
        if (!published && editable) {
            return $(
                `<span class="unpublishedBadge align-self-start flex-shrink-0 badge badge-pill ml-auto mt-1 border border-secondary text-secondary"><i title="Unpublished" class="fa fa-eye-slash" aria-hidden="true"></i> <i>Unpublished</i></span>`
            );
        }
        return null;
    }

    static onSelectChangeShowDetail(selectEl, insertEl, insertItems) {
        /*
        Generic helper function to listen when a user changes the item in a select element, and if
        an item is changed, then modify some content in a different location. Used for making
        django templates more interactive.
        */
        const $selectEl = $(selectEl),
            $insertEl = $(insertEl),
            $insertItems = $(insertItems),
            handleChange = () => {
                const selector = `#detail-${$selectEl.val()}`,
                    clone = $insertItems.find(selector).clone();
                $insertEl.fadeOut(() =>
                    $insertEl
                        .html(clone)
                        .trigger("select:change")
                        .fadeIn()
                );
            };
        $selectEl.on("change", handleChange).trigger("change");
    }

    static tablesort(el) {
        new Tablesort(el);
    }

    static bindCheckboxToPrefilter() {
        // show/hide prefilter based on checkbox selection
        const checkbox = $(this),
            input = $(`#id_prefilters-${checkbox.data("pf")}`),
            inputDiv = $(`#div_id_prefilters-${checkbox.data("pf")}`),
            hasItems = input.val().length > 0;

        checkbox.prop("checked", hasItems);
        checkbox
            .on("change", function() {
                inputDiv.toggle(checkbox.prop("checked"));
                if (checkbox.prop("checked") === false) {
                    input.val("");
                }
            })
            .trigger("change");
    }

    static dynamicFormListeners() {
        function compare(comparison, x, y) {
            // comparisons are done on flat arrays
            x = _.isArray(x) ? x : [x];
            y = _.isArray(y) ? y : [y];
            switch (comparison) {
                case "equals":
                    return _.isEqual(x, y);
                case "in":
                    return _.intersection(x, y).length > 0;
                case "contains":
                    return _.intersection(x, y).length === y.length;
            }
        }

        function getValue(el) {
            const type = $(el).attr("type");
            // checkbox/radio inputs return values based on checked property
            // and value attribute
            if (type === "checkbox" || type === "radio") {
                const value = $(el).attr("value"),
                    checked = $(el).prop("checked");
                // if the input has a value attribute...
                if (value !== undefined) {
                    // then the checked property determines
                    // whether to use this value attribute
                    return checked ? value : undefined;
                }
                // if there is no value attribute,
                // the checked property is used
                return checked;
            }
            // number inputs need to be parsed from their string value
            if (type === "number") {
                return parseFloat($(el).val());
            }
            // all other inputs return their computed value
            return $(el).val();
        }

        function getValues($inputs) {
            // get array of values from inputs
            return _.chain($inputs)
                .map(getValue)
                .filter(v => v !== undefined)
                .flatten()
                .value();
        }

        // conditions are passed into the django template as scripts
        const $ = window.$,
            $conditionsScripts = $('script[id^="conditions-"]');
        $conditionsScripts.remove(); // we only want these handled once, so remove them from dom
        for (const $conditions of $conditionsScripts) {
            // parse the conditions from script
            const conditions = JSON.parse($conditions.textContent);
            for (const condition of conditions) {
                const $subject = $(`#div_${condition.subject_id}`),
                    $subjectInput = $subject.find(":input");
                // add listeners on all inputs in the subject div
                $subjectInput.on("input", () => {
                    for (const observerId of condition.observer_ids) {
                        const $observer = $(`#div_${observerId}`),
                            $observerInput = $observer.find(":input"),
                            // get array of values from subject inputs
                            value = getValues($subjectInput),
                            // compare subject values against comparison value
                            check = compare(
                                condition.comparison,
                                value,
                                condition.comparison_value
                            ),
                            // determine whether observers should be shown or hidden
                            show = condition.behavior === "show" ? check : !check;
                        // hide the observer parent div (ie bootstrap column), and disable the observer inputs
                        $observer.parent().prop("hidden", !show);
                        $observerInput.prop("disabled", !show);
                    }
                });
                // trigger input on subject to hide/show based on initial data
                $subjectInput.trigger("input");
            }
        }
    }

    static addAnchorLinks(parent, selector) {
        $(parent)
            .find(selector)
            .each(function(index) {
                const id = $(this).attr("id");
                if (id) {
                    $(this).append(
                        `<a href="#${id}" class="ml-2 anchor-link" title="Section link"><span class="fa fa-fw fa-chain"></span></a>`
                    );
                }
            });
    }

    static hideElement(el, deleteEl) {
        const scrollVal = $(el).attr("scrolltop");
        deleteEl ? $(el).remove() : $(el).addClass("hidden");
        if (scrollVal) {
            $("body,html").animate({scrollTop: scrollVal}, 400);
        }
    }

    static addScrollHtmx(editClass, detailClass, deleteBtnId = null) {
        $("body").on("htmx:afterSwap", function(evt) {
            const elSwapOut = evt.detail.target,
                elSwapIn = evt.detail.elt,
                editElement = $(elSwapIn).hasClass(editClass)
                    ? elSwapIn
                    : $(elSwapIn)
                          .children("." + editClass)
                          .first();

            if ($(editElement).length && !$(editElement).hasClass("hidden")) {
                if ($(elSwapOut).hasClass(editClass)) {
                    // Maintain scroll attr between elements if source has a scollTop attr
                    // eg., if source and target are a form (failed update/create),
                    // otherwise set to current position.
                    const scrollTo = $(elSwapOut).attr("scrolltop") || $("body,html").scrollTop();
                    $(editElement).attr("scrolltop", scrollTo);
                } else {
                    // otherwise, set scroll attr to current scroll position so we can return later
                    const scrollTo = $("body,html").scrollTop();
                    $(editElement).attr("scrolltop", scrollTo);
                }
                // animate scroll to form
                const scrollTo = $(editElement).offset().top - 75;
                $("body,html").animate({scrollTop: scrollTo}, 500);
            } else {
                // if the form is being replaced by a read row, scroll to original position
                if (
                    $(elSwapIn).hasClass(detailClass) &&
                    $(elSwapOut).hasClass(editClass) &&
                    !$(elSwapIn).hasClass("clone")
                ) {
                    const scrollTo = $(elSwapOut).attr("scrolltop");
                    $("body,html").animate({scrollTop: scrollTo}, 500);
                }
            }
        });
        if (deleteBtnId) {
            $("body").on("htmx:afterRequest", function(evt) {
                // handle successful row deletion
                const elSwapOut = evt.detail.target,
                    targetEl = evt.detail.elt,
                    scrollPosition = $(elSwapOut).attr("scrolltop");
                if (targetEl.getAttribute("id") == deleteBtnId && evt.detail.successful) {
                    $("body,html").animate({scrollTop: scrollPosition}, 800);
                }
            });
        }
    }

    static watchForHtmx(selector) {
        // Process HTMX elements that are inserted into the DOM
        const target = document.querySelector(selector),
            observer = new MutationObserver(() => window.htmx.process(target));
        observer.observe(target, {subtree: true, childList: true});
    }
}
export default HAWCUtils;
