import textures from "textures";

export const NULL_CASE = "---";

export const createPattern = function(styles) {
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

        case "reverse stripes":
            return textures
                .lines()
                .orientation("6/8")
                .heavier()
                .stroke("white")
                .background(styles.fill);

        case "thin stripes":
            return textures
                .lines()
                .orientation("2/8")
                .heavier(2)
                .stroke(styles.fill)
                .background("white");

        case "thin reverse stripes":
            return textures
                .lines()
                .orientation("6/8")
                .heavier(2)
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
            throw `Unknown pattern: ${styles.pattern}`;
    }
};
