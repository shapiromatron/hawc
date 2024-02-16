import * as d3 from "d3";
import _ from "lodash";
import HAWCUtils from "shared/utils/HAWCUtils";
import textures from "textures";

import $ from "$";

const Patterns = {
        solid: "solid",
        stripes: "stripes",
        reverse_stripes: "reverse_stripes",
        vertical: "vertical",
        horizontal: "horizontal",
        diamonds: "diamonds",
        circles: "circles",
        woven: "woven",
        waves: "waves",
        hexagons: "hexagons",
    },
    createPattern = function(styles) {
        const pattern_fill = styles.pattern_fill || "#ffffff";
        switch (styles.pattern) {
            case Patterns.solid:
                return null;

            case Patterns.stripes:
                return textures
                    .lines()
                    .orientation("2/8")
                    .heavier()
                    .stroke(pattern_fill)
                    .background(styles.fill);

            case Patterns.reverse_stripes:
                return textures
                    .lines()
                    .orientation("6/8")
                    .heavier()
                    .stroke(pattern_fill)
                    .background(styles.fill);

            case Patterns.vertical:
                return textures
                    .lines()
                    .orientation("vertical")
                    .size(6)
                    .strokeWidth(4)
                    .stroke(styles.fill)
                    .background(pattern_fill);

            case Patterns.horizontal:
                return textures
                    .lines()
                    .orientation("horizontal")
                    .size(6)
                    .strokeWidth(4)
                    .stroke(styles.fill)
                    .background(pattern_fill);

            case Patterns.diamonds:
                return textures
                    .lines()
                    .orientation("2/8", "6/8")
                    .heavier()
                    .stroke(pattern_fill)
                    .background(styles.fill);

            case Patterns.circles:
                return textures
                    .circles()
                    .size(9)
                    .radius(3)
                    .fill(pattern_fill)
                    .background(styles.fill);

            case Patterns.woven:
                return textures
                    .paths()
                    .d("woven")
                    .stroke(pattern_fill)
                    .thicker()
                    .background(styles.fill);

            case Patterns.waves:
                return textures
                    .paths()
                    .d("waves")
                    .thicker()
                    .stroke(pattern_fill)
                    .background(styles.fill);

            case Patterns.hexagons:
                return textures
                    .paths()
                    .d("hexagons")
                    .size(6)
                    .strokeWidth(2)
                    .stroke(pattern_fill)
                    .background(styles.fill);

            default:
                console.error(`Unknown SVG pattern: ${styles.pattern}`);
                return null;
        }
    },
    applyStyles = (svg, el, styles) => {
        /**
         * Apply custom styling attributes to elements in an SVG
         * @param {svg} An svg element
         * @param {el} The element to apply the styles to
         * @param {styles} An object containing attributes to an element, string to string
         */
        const obj = el instanceof d3.transition || el instanceof d3.selection ? el : d3.select(el);
        _.each(styles, (value, attr) => {
            if (attr === "pattern") {
                const pattern = createPattern(styles);
                if (pattern) {
                    d3.select(svg).call(pattern);
                    obj.style("fill", pattern.url());
                }
            } else if (attr == "rotate") {
                obj.attr("transform", `rotate(${value} ${obj.attr("x")},${obj.attr("y")})`);
            } else {
                obj.style(attr, value);
            }
        });
    },
    handleVisualError = ($div, err, msg) => {
        console.error(err);
        if ($div === null) {
            const $el = $("#main-content-container h2").first();
            if ($el) {
                $div = $("<div>");
                $div.insertAfter($el);
            }
        }
        if (!msg) {
            msg = "Error: An error has ocurred; please check visualization settings.";
        }
        if ($div) {
            HAWCUtils.addAlert(msg, $div);
        } else {
            alert(msg);
        }
    };

export {applyStyles, handleVisualError, Patterns};
