import _ from "lodash";
import * as d3 from "d3";
import textures from "textures";

const createPattern = function(styles) {
    switch (styles.pattern) {
        case "solid":
            return null;

        case "stripes":
            return textures
                .lines()
                .orientation("2/8")
                .heavier()
                .stroke("white")
                .background(styles.fill);

        case "reverse_stripes":
            return textures
                .lines()
                .orientation("6/8")
                .heavier()
                .stroke("white")
                .background(styles.fill);

        case "thick_strips":
            return textures
                .lines()
                .orientation("3/8")
                .thicker()
                .stroke(styles.fill)
                .background("white");

        case "thick_reverse_strips":
            return textures
                .lines()
                .orientation("5/8")
                .thicker()
                .stroke(styles.fill)
                .background("white");

        case "diamonds":
            return textures
                .lines()
                .orientation("2/8", "6/8")
                .heavier()
                .stroke("white")
                .background(styles.fill);

        case "circles":
            return textures
                .circles()
                .size(9)
                .radius(3)
                .fill("white")
                .background(styles.fill);

        case "woven":
            return textures
                .paths()
                .d("woven")
                .stroke("white")
                .thicker()
                .background(styles.fill);

        case "waves":
            return textures
                .paths()
                .d("waves")
                .thicker()
                .stroke("white")
                .background(styles.fill);

        case "hexagons":
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
};

const applyStyles = (svg, el, styles) => {
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

export {applyStyles};
