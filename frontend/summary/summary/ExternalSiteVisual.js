import React from "react";
import ReactDOM from "react-dom";
import SmartTagContainer from "shared/smartTags/SmartTagContainer";
import HAWCModal from "shared/utils/HAWCModal";
import HAWCUtils from "shared/utils/HAWCUtils";

import BaseVisual from "./BaseVisual";
import {TABLEAU_HOSTNAME} from "./constants";
import TableauDashboard from "./TableauDashboard";

class ExternalWebsite extends BaseVisual {
    constructor(data) {
        super(data);
    }

    embedPage(el) {
        const settings = this.data.settings;

        if (settings.external_url_hostname === TABLEAU_HOSTNAME) {
            ReactDOM.render(
                <TableauDashboard
                    hostUrl={settings.external_url_hostname}
                    path={settings.external_url_path}
                    queryArgs={settings.external_url_query_args}
                />,
                el
            );
        } else {
            ReactDOM.render(
                <div className="alert alert-danger" role="alert">
                    Unable to render this page:
                    <br />
                    <a href={settings.external_url}>{settings.external_url}</a>
                </div>,
                el
            );
        }
    }

    addActionsMenu() {
        const actions = [
            "Additional actions",
            {url: this.data.settings.external_url, text: "View on native site"},
        ];
        if (window.isEditable) {
            actions.push(
                "Visualization editing",
                {url: this.data.url_update, text: "Update"},
                {url: this.data.url_delete, text: "Delete"}
            );
        }
        return HAWCUtils.pageActionsButton(actions);
    }

    displayAsPage($el, options) {
        var title = $("<h2>").text(this.data.title),
            captionDiv = $("<div>").html(this.data.caption),
            caption = new SmartTagContainer(captionDiv),
            $plotDiv = $("<div>");

        options = options || {};

        const actions = this.addActionsMenu();

        $el.empty().append($plotDiv);

        if (!options.visualOnly) {
            $el.prepend([actions, title]).append(captionDiv);
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
            .addHeader(
                $("<h4>")
                    .text(this.data.title)
                    .append(
                        `<span style="margin-left: 12px" title=${this.data.settings.external_url}>(<a target="_blank" href="${this.data.settings.external_url}">View <i class='fa fa-external-link'></i></a>)</span>`
                    )
            )
            .addBody([$plotDiv, captionDiv])
            .addFooter("")
            .show({maxWidth: 1200});
    }
}

export default ExternalWebsite;
