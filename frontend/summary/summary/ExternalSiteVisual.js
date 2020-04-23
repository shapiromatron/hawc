import React from "react";
import ReactDOM from "react-dom";

import SmartTagContainer from "assets/smartTags/SmartTagContainer";
import BaseVisual from "./BaseVisual";
import HAWCModal from "utils/HAWCModal";
import TableauDashboard from "./TableauDashboard";

import {TABLEAU_HOSTNAME} from "./constants";

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

    displayAsPage($el, options) {
        var title = $("<h1>")
                .text(this.data.title)
                .append(
                    `<span style="margin-left: 20px; font-size: 20px" title=${this.data.settings.external_url}>(<a target="_blank" href="${this.data.settings.external_url}">View <i class='fa fa-external-link'></i></a>)</span>`
                ),
            captionDiv = $("<div>").html(this.data.caption),
            caption = new SmartTagContainer(captionDiv),
            $plotDiv = $("<div>"),
            linkOut = $();

        options = options || {};

        if (window.isEditable) title.append(this.addActionsMenu());

        $el.empty().append($plotDiv);
        if (!options.visualOnly) $el.prepend([title, linkOut]).append(captionDiv);

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
        modal.getModal().on("shown", () => {
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
