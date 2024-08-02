export default {
    title: "Prisma Visual",
    sections: [
        {
            name: "Records",
            width: 10,
            height: 6,
            border_width: 2,
            rx: 50,
            ry: 5,
            bg_color: "White",
            border_color: "Black",
            font_color: "Black",
            text_style: "Left justified",
        },
    ],
    boxes: [
        {
            name: "References identified",
            width: 6,
            height: 4,
            border_width: 5,
            rx: 20,
            ry: 20,
            bg_color: "White",
            border_color: "Black",
            font_color: "Black",
            text_style: "Left justified",
            section: "Records",
        },
    ],
    bulleted_lists: [
        {
            name: "No Data Provided",
            width: 6,
            height: 4,
            border_width: 5,
            rx: 20,
            ry: 20,
            bg_color: "Yellow",
            border_color: "Black",
            font_color: "Black",
            box: "References identified",
            tag: 1,
        },
    ],
    cards: [
        {
            name: "No Data Provided",
            width: 6,
            height: 4,
            border_width: 5,
            rx: 20,
            ry: 20,
            bg_color: "Yellow",
            border_color: "Black",
            font_color: "Black",
            box: "References identified",
            tag: 1,
        },
    ],
    arrows: [
        {
            source: "References Identified",
            dest: "No Data Provided",
            width: 3,
            type: 2,
            color: "Black"
        }
    ],
};
