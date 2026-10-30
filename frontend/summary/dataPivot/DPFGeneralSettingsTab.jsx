import $ from "$";

import {_DataPivot_settings_general} from "./DataPivotUtilities";
import LegendSettings from "./DPFLegendSettings";

let build_settings_general_tab = function (self) {
    var tab = $('<div class="tab-pane" id="data_pivot_settings_general">'),
        build_general_settings = function () {
            var div = $("<div>"),
                tbl = $('<table class="table table-sm table-bordered">'),
                tbody = $("<tbody>"),
                colgroup = $('<colgroup><col style="width: 30%;"><col style="width: 70%;">');

            self._dp_settings_general = new _DataPivot_settings_general(
                self,
                self.settings.plot_settings
            );
            tbody.html(self._dp_settings_general.trs);
            tbl.html([colgroup, tbody]);
            return div.html(tbl);
        };

    const legendSettings = new LegendSettings(self);

    // update whenever tab is clicked
    self.$div.on("shown.bs.tab", 'a.dp_general_tab[data-toggle="tab"]', () =>
        legendSettings.update_legend()
    );

    self.legend = legendSettings.legend;

    return tab.html([build_general_settings(), "<hr>", legendSettings.render()]);
};

export default build_settings_general_tab;
