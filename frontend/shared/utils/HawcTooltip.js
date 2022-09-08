import $ from "$";

class HawcTooltip {
    constructor(styles) {
        // singleton instance
        var tooltip = $(".hawcTooltip"),
            heading,
            close;

        if (tooltip.length === 0) {
            close = $(
                '<button type="button" title="click or press ESC to close" class="close">&times;</button>'
            ).click(this.hide.bind(this));
            heading = $('<div class="popover-title" title="drag to reposition">')
                .append(close)
                .append('<div class="hawcTooltipHeading">');

            tooltip = $('<div class="hawcTooltip popover" style="display: none;">')
                .append(heading)
                .append('<div class="hawcTooltipContent popover-content">')
                .appendTo("body");
        }

        // reapply new styles
        this.tooltip = tooltip.css(styles || {});
    }

    _calculate_position(e) {
        // Determine the top and left coordinates for the popup box. Tries to put
        // to the right, then the left, then above, then below, and then finally if
        // none work, stick in the top-right corner.
        var top_padding = 55, // larger padding due to HAWC toolbar
            padding = 10,
            off_x = window.pageXOffset,
            off_y = window.pageYOffset,
            width = this.tooltip.width(),
            half_width = width / 2,
            height = this.tooltip.height(),
            half_height = height / 2,
            x = e.pageX - off_x,
            y = e.pageY - off_y,
            wh = window.innerHeight,
            ww = $("body").innerWidth(), // includes scrollbar
            l,
            t;

        if (x - width - padding > 0 || x + width + padding < ww) {
            // see if whole thing fits to left or right
            l = x + width + padding < ww ? x + padding : x - width - padding;
            t = y - half_height - top_padding > 0 ? y - half_height : top_padding;
            t = t + height + padding > wh ? wh - height - padding : t;
        } else if (y - height - top_padding > 0 || y + height + padding < wh) {
            // see if whole thing will fit above or below
            t = y - height - top_padding > 0 ? y - height - padding : y + padding;
            l = x - half_width > 0 ? x - half_width : 0;
            l = l + width + padding > ww ? ww - width - padding : l;
        } else {
            // put at top-right of window
            t = top_padding;
            l = ww - width - padding;
        }

        return {top: `${t + off_y}px`, left: `${l + off_x}px`};
    }

    hide() {
        this.tooltip.fadeOut("slow");
        $(document).unbind("keyup");
    }

    show(e, title, content) {
        this.tooltip.find(".hawcTooltipHeading").html(title);
        this.tooltip.find(".hawcTooltipContent").html(content);
        this.tooltip
            .css(this._calculate_position(e))
            .fadeIn("slow")
            .scrollTop();

        var showTooltip = function(e) {
            e.stopPropagation();
            if (e.keyCode === 27) {
                this.hide();
            }
        };

        $(document).bind("keyup", showTooltip.bind(this));
    }
}

export default HawcTooltip;
