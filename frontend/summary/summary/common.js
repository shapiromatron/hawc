import _ from "lodash";
import * as d3 from "d3";
import textures from "textures";

const Patterns = {
        solid: "solid",
        stripes: "stripes",
        reverse_stripes: "reverse_stripes",
        thick_strips: "thick_strips",
        thick_reverse_strips: "thick_reverse_strips",
        diamonds: "diamonds",
        circles: "circles",
        woven: "woven",
        waves: "waves",
        hexagons: "hexagons",
    },
    createPattern = function(styles) {
        switch (styles.pattern) {
            case Patterns.solid:
                return null;

            case Patterns.stripes:
                return textures
                    .lines()
                    .orientation("2/8")
                    .heavier()
                    .stroke("white")
                    .background(styles.fill);

            case Patterns.reverse_stripes:
                return textures
                    .lines()
                    .orientation("6/8")
                    .heavier()
                    .stroke("white")
                    .background(styles.fill);

            case Patterns.thick_strips:
                return textures
                    .lines()
                    .orientation("3/8")
                    .thicker()
                    .stroke(styles.fill)
                    .background("white");

            case Patterns.thick_reverse_strips:
                return textures
                    .lines()
                    .orientation("5/8")
                    .thicker()
                    .stroke(styles.fill)
                    .background("white");

            case Patterns.diamonds:
                return textures
                    .lines()
                    .orientation("2/8", "6/8")
                    .heavier()
                    .stroke("white")
                    .background(styles.fill);

            case Patterns.circles:
                return textures
                    .circles()
                    .size(9)
                    .radius(3)
                    .fill("white")
                    .background(styles.fill);

            case Patterns.woven:
                return textures
                    .paths()
                    .d("woven")
                    .stroke("white")
                    .thicker()
                    .background(styles.fill);

            case Patterns.waves:
                return textures
                    .paths()
                    .d("waves")
                    .thicker()
                    .stroke("white")
                    .background(styles.fill);

            case Patterns.hexagons:
                return textures
                    .paths()
                    .d("hexagons")
                    .size(6)
                    .strokeWidth(2)
                    .stroke("white")
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
    };

export {Patterns, applyStyles};
