import $ from "$";

let build_styles_tab = function (self) {
    var tab = $('<div class="tab-pane" id="data_pivot_settings_styles">'),
        symbol_div = self.style_manager.build_styles_crud("symbols"),
        line_div = self.style_manager.build_styles_crud("lines"),
        text_div = self.style_manager.build_styles_crud("texts"),
        rectangle_div = self.style_manager.build_styles_crud("rectangles");

    return tab.html([symbol_div, "<hr>", line_div, "<hr>", text_div, "<hr>", rectangle_div]);
};

export default build_styles_tab;
