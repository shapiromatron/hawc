import _ from "lodash";

import $ from "$";

class HAWCModal {
    constructor() {
        // singleton modal instance
        var $modalDiv = $("#hawcModal");
        if ($modalDiv.length === 0) {
            $modalDiv = $(
                '<div id="hawcModal" class="modal fade" tabindex="-1" role="dialog" data-backdrop="static"></div>'
            )
                .append(
                    $('<div class="modal-dialog" role="document">').append(
                        $('<div class="modal-content">')
                            .append('<div class="modal-header"></div>')
                            .append('<div class="modal-body"></div>')
                            .append('<div class="modal-footer"></div>')
                    )
                )
                .appendTo($("body"));
            $(window).on("resize", this._resizeModal.bind(this));
        }
        this.$modalDiv = $modalDiv;
    }

    show(options, cb) {
        this.fixedSize = (options && options.fixedSize) || false;
        this.maxWidth = (options && options.maxWidth) || Infinity;
        this.maxHeight = (options && options.maxHeight) || Infinity;
        this._resizeModal();
        this.getBody().scrollTop(0);
        if (cb) {
            this.$modalDiv.on("shown.bs.modal", cb);
        }
        this.$modalDiv.modal("show");
        return this;
    }

    hide() {
        this.$modalDiv.modal("hide");
        return this;
    }

    addHeader(html, options) {
        var noClose = (options && options.noClose) || false,
            $el = this.$modalDiv.find(".modal-header");
        $el.html(html);
        if (!noClose)
            $el.append(
                '<button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button>'
            );
        return this;
    }

    addTitleLinkHeader(name, url, options) {
        return this.addHeader(`<h4><a href="${url}" target="_blank">${name}</a></h4>`, options);
    }

    addFooter(html, options) {
        var noClose = (options && options.noClose) || false,
            $el = this.$modalDiv.find(".modal-footer");
        $el.html(html);
        if (!noClose)
            $el.append('<button class="btn btn-light" data-dismiss="modal">Close</button>');
        return this;
    }

    getBody() {
        return this.$modalDiv.find(".modal-body");
    }

    addBody(html) {
        this.getBody()
            .html(html)
            .scrollTop(0);
        return this;
    }

    _resizeModal() {
        var h = parseInt($(window).height(), 10),
            w = parseInt($(window).width(), 10),
            modalContentCSS = {
                width: "",
                height: "",
                top: "",
                left: "",
                margin: "",
                "max-height": "",
            },
            modalBodyCSS = {
                "max-height": "",
            };

        if (!this.fixedSize) {
            var mWidth = Math.min(w - 50, this.maxWidth),
                mWidthPadding = parseInt((w - mWidth) * 0.5, 10),
                mHeight = Math.min(h - 50, this.maxHeight);
            _.extend(modalContentCSS, {
                width: `${mWidth}px`,
                top: "25px",
                left: `${mWidthPadding}px`,
                margin: "0px",
                "max-height": `${mHeight}px`,
            });
            _.extend(modalBodyCSS, {
                "max-height": `${mHeight - 150}px`,
            });
        }
        this.$modalDiv.find("modal-content").css(modalContentCSS);
        this.getBody().css(modalBodyCSS);
    }

    getModal() {
        return this.$modalDiv;
    }
}

export default HAWCModal;
