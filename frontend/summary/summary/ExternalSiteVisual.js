import React from "react";
import {createRoot} from "react-dom/client";
import SmartTagContainer from "shared/smartTags/SmartTagContainer";
import HAWCModal from "shared/utils/HAWCModal";
import HAWCUtils from "shared/utils/HAWCUtils";

import BaseVisual from "./BaseVisual";
import TableauDashboard from "./TableauDashboard";
import {addLabelAction, addLabelIndicators} from "./common";
import {TABLEAU_HOSTNAME} from "./constants";

class ExternalWebsite extends BaseVisual {
    constructor(data) {
        super(data);
    }

    embedPage(el) {
        const settings = this.data.settings;

        if (settings.external_url_hostname === TABLEAU_HOSTNAME) {
            const root = createRoot(el);
            root.render(
                <TableauDashboard
                    hostUrl={settings.external_url_hostname}
                    path={settings.external_url_path}
                    queryArgs={settings.external_url_query_args}
                    filters={settings.filters}
                />
            );
        } else {
            const root = createRoot(el);
            root.render(
                <div className="alert alert-danger" role="alert">
                    Unable to render this page:
                    <br />
                    <a href={settings.external_url}>{settings.external_url}</a>
                </div>
            );
        }
    }

    addActionsMenu() {
        const actions = [
            "Additional actions",
            {href: this.data.settings.external_url, text: "View on native site"},
        ];
        if (window.isEditable) {
            actions.push(
                "Visualization editing",
                {href: this.data.url_update, text: "Update"},
                {href: this.data.url_delete, text: "Delete"},
                addLabelAction(this.data.label_htmx)
            );
        }
        return HAWCUtils.pageActionsButton(actions);
    }

    displayAsPage($el, options) {
        var title = $("<h2>").text(this.data.title),
            labelIndicators = addLabelIndicators(this.data.label_indicators_htmx),
            captionDiv = $("<div>").html(this.data.caption),
            caption = new SmartTagContainer(captionDiv),
            $plotDiv = $("<div>");

        options = options || {};

        const actions = this.addActionsMenu();

        $el.empty().append($plotDiv);

        if (!options.visualOnly) {
            var headerRow = $('<div class="d-flex">').append([
                title,
                labelIndicators,
                HAWCUtils.unpublished(this.data.published, window.isEditable),
                actions,
            ]);
            $el.prepend(headerRow).append(captionDiv);
        }

        this.embedPage($plotDiv[0]);
        caption.renderAndEnable();
        return this;
    }

    displayAsModal(options) {
        options = options || {};
        var captionDiv = $("<div>").html(this.data.caption),
            caption = new SmartTagContainer(captionDiv),
            $plotDiv = $("<div>"),
            modal = new HAWCModal();
        modal.getModal().on("shown.bs.modal", () => {
            caption.renderAndEnable();
            this.embedPage($plotDiv[0]);
        });
        modal
            .addHeader([
                $("<h4>")
                    .text(this.data.title)
                    .append(
                        `<span style="margin-left: 12px" title=${this.data.settings.external_url}>(<a target="_blank" href="${this.data.settings.external_url}">View <i class='fa fa-external-link'></i></a>)</span>`
                    ),
                HAWCUtils.unpublished(this.data.published, window.isEditable),
            ])
            .addBody([$plotDiv, captionDiv])
            .addFooter("")
            .show({maxWidth: 1200});
    }
}

export default ExternalWebsite;
