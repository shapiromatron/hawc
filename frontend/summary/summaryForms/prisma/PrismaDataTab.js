import $ from "$";


let buildHeaderTr = function (lst) {
    return $("<tr>").html(lst.map(v => `<th>${v}</th>`).join());
},
    buildColGroup = function (widths) {
        return $("<colgroup>").html(widths.map(width => `<col width=${width}></col>`).join(""));
    };

class _Prisma_sections_row {

    constructor(prisma, values) {
        this.prisma = prisma;
        this.values = values;

        // TODO create html row

        this.data_push();
        return this;
    }

    static defaults = function() {
        return {
            name: "",
            width: 10,
            height: 6,
            border_width: 2,
            rx: 0,
            ry: 0,
            bg_color: "White",
            border_color: "Black",
            font_color: "Black",
            text_style: "Left justified"
        }
    }

    data_push() {
        // TODO
    }

}

let buildSectionsTable = function (tab, prisma) {
    let thead = $("<thead>").html(
        buildHeaderTr([
            "Name",
            "Width",
            "Height",
            "Border Width",
            "rx",
            "ry",
            "Background color",
            "Border color",
            "Font color",
            "Text Formatting Style"
        ])
    ),
        tbody = $("<tbody>"),
        colgroup = buildColGroup(["", "", "", "150px", "", "120px"]), // TODO: define colgroup properly
        tbl = $('<table class="table table-sm table-bordered">').html([thead, tbody]),
        settings = prisma.sections,
        addDataRow = function (i) {
            let obj;
            if (!settings[i]) {
                settings.push(_Prisma_sections_row.defaults());
            }
            obj = new _Prisma_sections_row(prisma, settings[i]);
            tbody.append(obj.tr);
        },
        newDataRow = function () {
            let num_rows = settings.length;
            addDataRow(num_rows);
        },
        newRowBtn = $(
            '<button class="btn btn-primary float-right"><i class="fa fa-fw fa-plus"></i>&nbsp;Add row</button>'
        ).on("click", newDataRow),
        numRows = settings.length === 0 ? 3 : settings.length;

    for (var i = 0; i < numRows; i++) {
        addDataRow(i);
    }

    tab.append([newRowBtn, $("<h3>Data point options</h3>")]);
    tab.append(tbl);
},
buildTab = function(prisma) {
    let tab = $('<div class="tab-pane" id="prisma_settings_data">')
    buildSectionsTable(tab, prisma)
};

export default buildTab;
