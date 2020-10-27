import $ from "$";

import DataPivot from "summary/dataPivot/DataPivot";
import Endpoint from "animal/Endpoint";
import Study from "study/Study";
import Visual from "summary/summary/Visual";

class InlineRendering {
    constructor(div) {
        this.$div = $(div);
        this.type = this.$div.data("type");
        this.pk = this.$div.data("pk");
        this.$div.data("_smartTag", this);
    }

    render() {
        this.renderParent = $('<div class="inlineSmartTagParent">').insertBefore(this.$div);

        let $title = $('<div class="row inlineSmartTagTitle">'),
            $body = $('<div class="row inlineSmartTagBody">'),
            $caption = $('<div class="row inlineSmartTagCaption">').append(this.$div.detach()),
            $container = $('<div class="inlineSmartTagContainer container-fluid">').append([
                $title,
                $body,
                $caption,
            ]);

        this.renderParent.append($container);

        this.$div.removeClass("active");
        this.display(this.getModelClass());
        this.rendered = true;
    }

    unrender() {
        this.$div.insertBefore(this.inline);
        this.inline.remove();
        this.$div.addClass("active");
        this.rendered = false;
    }

    setTitle($titleContent) {
        let $title = this.renderParent.find(".inlineSmartTagTitle"),
            $body = this.renderParent.find(".inlineSmartTagBody"),
            expandHideTogger = function() {
                let isMax = $title.find(".icon-minus").length === 1;
                if (isMax) {
                    $title
                        .find(".icon-minus")
                        .removeClass("icon-minus")
                        .addClass("icon-plus");
                    $body.fadeOut("slow");
                } else {
                    $title
                        .find(".icon-plus")
                        .removeClass("icon-plus")
                        .addClass("icon-minus");
                    $body.fadeIn("slow");
                }
            },
            toggleBtn = $('<a title="click to toggle visibility" class="btn btn-xs pull-right">')
                .append('<i class="icon-minus"></i>')
                .off("click")
                .click(expandHideTogger.bind(this));

        $title.append($titleContent.prepend(toggleBtn));
    }

    setBody($content) {
        this.renderParent.find(".inlineSmartTagBody").append($content);
    }

    getModelClass() {
        let map = {
                endpoint: Endpoint,
                study: Study,
                visual: Visual,
                data_pivot: DataPivot,
            },
            Cls = map[this.type];
        if (!Cls) {
            throw `Unknown class: ${this.type}`;
        }
        return Cls;
    }

    display(Cls) {
        Cls.displayInline(this.pk, this.setTitle.bind(this), this.setBody.bind(this));
    }
}

export default InlineRendering;
