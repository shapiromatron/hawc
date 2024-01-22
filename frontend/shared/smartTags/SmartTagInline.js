import Endpoint from "animal/Endpoint";
import Study from "study/Study";
import DataPivot from "summary/dataPivot/DataPivot";
import Visual from "summary/summary/Visual";

import $ from "$";

class InlineRendering {
    constructor(div) {
        this.$div = $(div);
        this.type = this.$div.data("type");
        this.pk = this.$div.data("pk");
        this.$div.data("_smartTag", this);
    }

    render() {
        this.renderParent = $('<div class="inlineSmartTagParent">').insertBefore(this.$div);

        let $title = $('<div class="card-header inlineSmartTagTitle">'),
            $body = $('<div class="card-body inlineSmartTagBody">'),
            $caption = $('<div class="card-footer inlineSmartTagCaption">').append(
                this.$div.detach()
            ),
            $container = $('<div class="inlineSmartTagContainer card">').append([
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
            expandHideTogger = function () {
                let isMax = $title.find(".fa-minus").length === 1;
                if (isMax) {
                    $title.find(".fa-minus").removeClass("fa-minus").addClass("fa-plus");
                    $body.fadeOut("slow");
                } else {
                    $title.find(".fa-plus").removeClass("fa-plus").addClass("fa-minus");
                    $body.fadeIn("slow");
                }
            },
            toggleBtn = $('<a title="click to toggle visibility" class="btn btn-sm float-right">')
                .append('<i class="fa fa-minus"></i>')
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
