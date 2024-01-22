import _ from "lodash";
import HAWCUtils from "shared/utils/HAWCUtils";

import $ from "$";

class BaseVisualForm {
    constructor($el, config) {
        this.$el = $el;
        this.config = config;
        this.fields = [];
        this.settings = {};
        this.initDataForm();
        this.initSettings();
        this.buildSettingsForm();
        this.getData();
        this.setupEvents();
    }

    setupEvents() {
        var self = this,
            setDataChanged = function () {
                self.dataSynced = false;
            },
            $data = this.$el.find("#data"),
            $settings = this.$el.find("#settings"),
            $preview = this.$el.find("#preview");

        // check if any data have changed
        $data.find(":input").on("change", setDataChanged);

        // whenever data is synced, rebuild
        $settings.on("dataSynced", this.unpackSettings.bind(this));
        $preview.on("dataSynced", this.buildPreviewDiv.bind(this));

        $('a[data-toggle="tab"]').on("show.bs.tab", function (e) {
            var toShow = $(e.target).attr("href"),
                shown = $(e.relatedTarget).attr("href");

            switch (shown) {
                case "#data":
                    self.dataSynced ? self.unpackSettings() : self.getData();
                    break;
                case "#settings":
                    self.packSettings();
                    break;
                case "#preview":
                    self.removePreview();
                    break;
            }

            switch (toShow) {
                case "#settings":
                    if (!self.dataSynced) {
                        self.addSettingsLoader();
                        self.getData();
                    }
                    break;
                case "#preview":
                    self.setPreviewLoading();
                    if (self.dataSynced) {
                        $('a[data-toggle="tab"]').one(
                            "shown.bs.tab",
                            self.buildPreviewDiv.bind(self)
                        );
                    } else {
                        self.getData();
                    }
                    break;
            }
        });

        $("#data form").on("submit", this.packSettings.bind(this));
    }

    getData() {
        var self = this,
            form = $("form").serialize();

        if (this.isSynching) return;
        this.dataSynced = false;
        this.isSynching = true;
        $.post(this.config.preview_url, form, function (d) {
            self.data = d;
            if (self.afterGetDataHook) self.afterGetDataHook(d);
        })
            .fail(function () {
                HAWCUtils.addAlert(
                    "<strong>Data request failed.</strong> Sorry, your query to return results for the visualization failed; please contact the HAWC administrator if you feel this was an error which should be fixed."
                );
            })
            .always(function () {
                self.isSynching = false;
                self.dataSynced = true;
                $("#preview, #settings").trigger("dataSynced");
            });
    }

    initSettings() {
        var settings;
        try {
            settings = JSON.parse($("#id_settings").val());
        } catch (err) {
            settings = {};
        }

        // set defaults if needed
        this.constructor.schema.forEach(function (d) {
            if (d.name && settings[d.name] === undefined) settings[d.name] = d.def;
        });

        $("#id_settings").val(JSON.stringify(settings));
        this.settings = settings;
    }

    packSettings() {
        // settings-tab -> #id_settings serialization
        this.fields.map(function (d) {
            d.toSerialized();
        });
        $("#id_settings").val(JSON.stringify(this.settings));
    }

    unpackSettings() {
        // #id_settings serialization -> settings-tab
        // must also have synced data
        this.removeSettingsLoader();
        var self = this,
            settings;
        try {
            settings = JSON.parse($("#id_settings").val());
            _.each(settings, function (val, key) {
                if (self.settings[key] !== undefined) {
                    self.settings[key] = val;
                }
            });
        } catch (err) {
            // run anyways
        }
        this.fields.forEach(d => d.fromSerialized());
    }

    buildSettingsForm() {
        var $parent = this.$el.find("#settings"),
            self = this,
            getParent = function (val) {
                return self.settingsTabs[val] || $parent;
            };

        this.buildSettingsSubtabs($parent);

        this.constructor.schema.forEach(function (d) {
            let Cls = d.type;
            self.fields.push(new Cls(d, getParent(d.tab), self));
        });

        this.fields.forEach(function (d) {
            d.render();
        });
        this.addPsuedoSubmitDiv($parent, this.packSettings);
    }

    addPsuedoSubmitDiv($parent, beforeSubmit) {
        var self = this,
            submitter = this.$el.find("#data .form-actions input"),
            cancel_url = this.$el.find("#data .form-actions a").attr("href");

        $('<div class="form-actions">')
            .append(
                $('<a class="btn btn-primary">Save</a>').on("click", function () {
                    if (beforeSubmit) beforeSubmit.call(self);
                    submitter.trigger("click");
                })
            )
            .append(`<a class="btn btn-secondary mx-2" href="${cancel_url}">Cancel</a>`)
            .appendTo($parent);
    }

    buildSettingsSubtabs($parent) {
        var self = this,
            tabs = this.constructor.tabs || [],
            tablinks = [],
            isActive;

        this.settingsTabs = {};

        if (tabs.length === 0) return;

        _.each(tabs, function (d, i) {
            isActive = i === 0 ? "active" : "";
            self.settingsTabs[d.name] = $(
                `<div id="settings_${d.name}" class="tab-pane ${isActive}">`
            );
            tablinks.push(
                `<a class="nav-link ${isActive}" href="#settings_${d.name}" data-toggle="tab">${d.label}</a>`
            );
        });

        $('<nav class="nav nav-tabs">').append(tablinks).appendTo($parent);

        $('<div class="tab-content">').append(_.values(self.settingsTabs)).appendTo($parent);
    }

    setPreviewLoading() {
        var $preview = this.$el.find("#preview"),
            loading = HAWCUtils.loading();
        $preview.html(loading);
    }

    addSettingsLoader() {
        var div = $("#settings"),
            loader = div.find("p.loader");
        if (loader.length === 0) {
            loader = HAWCUtils.loading();
        }
        div.children().hide(0, function () {
            div.append(loader).show();
        });
    }

    removeSettingsLoader() {
        var div = $("#settings");
        div.find("p.loader").remove();
        div.children().show(800);
    }

    initDataForm() {}

    buildPreviewDiv() {
        var $el = $("#preview"),
            data = $.extend(true, {}, this.data);

        data.settings = $.extend(false, {}, this.settings);
        this.buildPreview($el, data);
        this.addPsuedoSubmitDiv($el, this.updateSettingsFromPreview);
    }

    buildPreview() {
        return HAWCUtils.abstractMethod();
    }

    removePreview() {
        this.updateSettingsFromPreview();
        $("#preview").empty();
        delete this.preview;
    }

    updateSettingsFromPreview() {
        return HAWCUtils.abstractMethod();
    }
}

export default BaseVisualForm;
