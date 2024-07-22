import $ from "$";


let buildHeaderTr = function (lst) {
    return $("<tr>").html(lst.map(v => `<th>${v}</th>`).join());
},
    buildColGroup = function (widths) {
        return $("<colgroup>").html(widths.map(width => `<col width=${width}></col>`).join(""));
    };

let buildBoxesTable = function (tab, prisma) {
    let thead = $("<thead>").html(
        buildHeaderTr([
            "Column header",
            "Legend name",
            "Marker style",
            "Conditional formatting",
            "On-click",
            "Ordering",
        ])
    ),
        tbody = $("<tbody>"),
        colgroup = buildColGroup(["", "", "", "150px", "", "120px"]),
        tbl = $('<table class="table table-sm table-bordered">').html([thead, colgroup, tbody]),
        settings = prisma.settings.datapoint_settings,
        addDataRow = function (i) {
            let obj;
            if (!settings[i]) {
                settings.push(_DataPivot_settings_pointdata.defaults());
            }
            obj = new _DataPivot_settings_pointdata(prisma, settings[i]);
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
    let tab = $('<div class="tab-pane" id="data_pivot_settings_data">')
    buildBoxesTable(tab, prisma)
};

export default buildTab;
