var InputField = function(schema, $parent, parent){
    this.$parent = $parent;
    this.schema = schema;
    this.parent = parent;
    return this;
};
_.extend(InputField.prototype, {
    toSerialized: HAWCUtils.abstractMethod,
    fromSerialized: HAWCUtils.abstractMethod,
    render: HAWCUtils.abstractMethod
});


var TableField = function () {
    return InputField.apply(this, arguments);
}
_.extend(TableField.prototype, InputField.prototype, {
    renderHeader: HAWCUtils.abstractMethod,
    addRow: HAWCUtils.abstractMethod,
    fromSerializedRow: HAWCUtils.abstractMethod,
    toSerializedRow: HAWCUtils.abstractMethod,
    toSerialized: function () {
        this.parent.settings[this.schema.name] =
            _.map(this.$tbody.children(), this.toSerializedRow, this);
    },
    fromSerialized: function () {
        var arr = this.parent.settings[this.schema.name] || [];
        this.$tbody.empty();
        if (arr.length === 0) {
            this.addRow();
        } else {
            _.each(arr, this.fromSerializedRow, this);
        }
    },
    setColgroup: function () {
        var cw = this.schema.colWidths || [],
            setCol = function(d){return '<col width="{0}%"'.printf(d);};
        $("<colgroup>")
            .append(_.map(cw, setCol))
            .appendTo(this.table);
    },
    render: function () {
        var $div = $('<div class="control-group form-row">');

        if (this.schema.prependSpacer) new SpacerNullField(this.schema, this.$parent).render();
        if (this.schema.label) new HeaderNullField(this.schema, this.$parent).render();

        this.table = $('<table class="table table-condensed table-bordered">').appendTo($div);
        this.setColgroup();
        this.$thead = $('<thead>').appendTo(this.table);
        this.$tbody = $('<tbody>').appendTo(this.table);
        this.renderHeader();
        $div.appendTo(this.$parent);
    },
    thOrdering: function (options) {
        var th = $('<th>').html("Ordering&nbsp;"),
            add = $('<button class="btn btn-mini btn-primary" title="Add row"><i class="icon-plus icon-white"></button>')
                    .on('click', $.proxy(this.addRow, this));

        if (options.showNew) th.append(add);
        return th;
    },
    tdOrdering: function () {
        var moveUp = function(){
                var tr = $(this.parentNode.parentNode),
                    prev = tr.prev();
                if (prev.length>0) tr.insertBefore(prev);
            },
            moveDown = function(){
                var tr = $(this.parentNode.parentNode),
                    next = tr.next();
                if (next.length>0) tr.insertAfter(next);
            },
            del = function(){
                $(this.parentNode.parentNode).remove();
            },
            td = $('<td>');

        td.append(
            $('<button class="btn btn-mini" title="Move up"><i class="icon-arrow-up"></button>').on('click', moveUp),
            $('<button class="btn btn-mini" title="Move down"><i class="icon-arrow-down"></button>').on('click', moveDown),
            $('<button class="btn btn-mini" title="Remove"><i class="icon-remove"></button>').on('click', del)
        );
        return td;
    },
    addTdText: function(name, val){
        val = (val!==undefined) ? val : "";
        return '<td><input name="{0}" value="{1}" class="span12" type="text"></td>'.printf(name, val);
    },
    addTdInt: function(name, val){
        val = (val!==undefined) ? val : "";
        return '<td><input name="{0}" value="{1}" class="span12" type="number"></td>'.printf(name, val);
    },
    addTdFloat: function(name, val){
        val = (val!==undefined) ? val : "";
        return '<td><input name="{0}" value="{1}" class="span12" type="number" step="any"></td>'.printf(name, val);
    },
    addTdSelect: function(name, values){
        var sel = $('<select name="{0}" class="span12">'.printf(name))
                .append(_.map(values, function(d){return '<option value="{0}">{0}</option>'.printf(d)}));
        return $('<td>').append(sel);
    },
    addTdSelectMultiple: function(name, values){
        var sel = $('<select name="{0}" class="span12" multiple>'.printf(name))
                .append(_.map(values, function(d){return '<option value="{0}">{0}</option>'.printf(d)}));
        return $('<td>').append(sel);
    }
});


var ReferenceLineField = function () {
    return TableField.apply(this, arguments);
}
_.extend(ReferenceLineField.prototype, TableField.prototype, {
    renderHeader: function () {
        return $('<tr>')
            .append(
                '<th>Line value</th>',
                '<th>Caption</th>',
                '<th>Style</th>',
                this.thOrdering({showNew: true})
            ).appendTo(this.$thead);
    },
    addRow: function () {
        return $('<tr>')
            .append(
                this.addTdFloat('value'),
                this.addTdText('title'),
                this.addTdSelect('style', _.pluck(D3Visualization.styles.lines, 'name')),
                this.tdOrdering()
            ).appendTo(this.$tbody);
    },
    fromSerializedRow: function (d,i) {
        var row = this.addRow();
        row.find('input[name="value"]').val(d.value);
        row.find('input[name="title"]').val(d.title);
        row.find('select[name="style"]').val(d.style);
    },
    toSerializedRow: function (row) {
        row = $(row);
        return {
            "value": parseFloat(row.find('input[name="value"]').val(), 10),
            "title": row.find('input[name="title"]').val(),
            "style": row.find('select[name="style"]').val(),
        }
    }
});


var ReferenceRangeField = function () {
    return TableField.apply(this, arguments);
}
_.extend(ReferenceRangeField.prototype, TableField.prototype, {
    renderHeader: function () {
        return $('<tr>')
            .append(
                '<th>Lower value</th>',
                '<th>Upper value</th>',
                '<th>Caption</th>',
                '<th>Style</th>',
                this.thOrdering({showNew: true})
            ).appendTo(this.$thead);
    },
    addRow: function () {
        return $('<tr>')
            .append(
                this.addTdFloat('lower'),
                this.addTdFloat('upper'),
                this.addTdText('title'),
                this.addTdSelect('style', _.pluck(D3Visualization.styles.rectangles, 'name')),
                this.tdOrdering()
            ).appendTo(this.$tbody);
    },
    fromSerializedRow: function (d,i) {
        var row = this.addRow();
        row.find('input[name="lower"]').val(d.lower);
        row.find('input[name="upper"]').val(d.upper);
        row.find('input[name="title"]').val(d.title);
        row.find('select[name="style"]').val(d.style);
    },
    toSerializedRow: function (row) {
        row = $(row);
        return {
            "lower": parseFloat(row.find('input[name="lower"]').val(), 10),
            "upper": parseFloat(row.find('input[name="upper"]').val(), 10),
            "title": row.find('input[name="title"]').val(),
            "style": row.find('select[name="style"]').val(),
        }
    }
});


var ReferenceLabelField = function () {
    return TableField.apply(this, arguments);
}
_.extend(ReferenceLabelField.prototype, TableField.prototype, {
    renderHeader: function () {
        return $('<tr>')
            .append(
                '<th>Caption</th>',
                '<th>Style</th>',
                '<th>X position</th>',
                '<th>Y position</th>',
                this.thOrdering({showNew: true})
            ).appendTo(this.$thead);
    },
    addRow: function () {
        return $('<tr>')
            .append(
                this.addTdText('caption'),
                this.addTdSelect('style', _.pluck(D3Visualization.styles.texts, 'name')),
                this.addTdInt('x', 0),
                this.addTdInt('y', 0),
                this.tdOrdering()
            ).appendTo(this.$tbody);
    },
    fromSerializedRow: function (d,i) {
        var row = this.addRow();
        row.find('input[name="caption"]').val(d.caption);
        row.find('select[name="style"]').val(d.style);
        row.find('input[name="x"]').val(d.x);
        row.find('input[name="y"]').val(d.y);
    },
    toSerializedRow: function (row) {
        row = $(row);
        return {
            "caption": row.find('input[name="caption"]').val(),
            "style": row.find('select[name="style"]').val(),
            "x": parseInt(row.find('input[name="x"]').val(), 10),
            "y": parseInt(row.find('input[name="y"]').val(), 10),
        }
    }
});


var TextField = function () {
    return InputField.apply(this, arguments);
}
_.extend(TextField.prototype, InputField.prototype, {
    toSerialized: function () {
        this.parent.settings[this.schema.name] = this.$inp.val();
    },
    fromSerialized: function () {
        this.$inp.val(this.parent.settings[this.schema.name]);
    },
    _setInput: function(){
        this.$inp = $('<input type="text" name="{0}" class="span12" required>'.printf(this.schema.name));
    },
    render: function () {
        this._setInput();
        var $ctrl = $('<div class="controls">').append(this.$inp);

        if(this.schema.helpText)
            $ctrl.append('<span class="help-inline">{0}</span>'.printf(this.schema.helpText));

        var $div = $('<div class="control-group form-row">')
                .append('<label class="control-label">{0}:</label>'.printf(this.schema.label))
                .append($ctrl);

        this.$parent.append($div);
    }
});


var IntegerField = function () {
    return TextField.apply(this, arguments);
}
_.extend(IntegerField.prototype, TextField.prototype, {
    toSerialized: function () {
        this.parent.settings[this.schema.name] = parseInt(this.$inp.val(), 10);
    },
    _setInput: function(){
        this.$inp = $('<input type="number" name="{0}" class="span12" required>'.printf(this.schema.name));
    },
});


var FloatField = function () {
    return TextField.apply(this, arguments);
}
_.extend(FloatField.prototype, TextField.prototype, {
    toSerialized: function () {
        this.parent.settings[this.schema.name] = parseFloat(this.$inp.val(), 10);
    },
    _setInput: function(){
        this.$inp = $('<input type="number" step="any" name="{0}" class="span12" required>'.printf(this.schema.name));
    },
});


var CheckboxField = function () {
    return TextField.apply(this, arguments);
}
_.extend(CheckboxField.prototype, TextField.prototype, {
    toSerialized: function () {
        this.parent.settings[this.schema.name] = this.$inp.prop('checked');
    },
    fromSerialized: function () {
        this.$inp.prop('checked', this.parent.settings[this.schema.name]);
    },
    _setInput: function(){
        this.$inp = $('<input type="checkbox" name="{0}">'.printf(this.schema.name));
    },
});


var SelectField = function () {
    return TextField.apply(this, arguments);
}
_.extend(SelectField.prototype, TextField.prototype, {
    _setInput: function(){
        var makeOpt = function(d){return '<option value="{0}">{1}</option>'.printf(d[0], d[1]); };
        this.$inp = $('<select name="{0}" class="span12">'.printf(this.schema.name))
            .html( this.schema.opts.map(makeOpt).join("") );
    },
});


var SpacerNullField = function () {
    return TextField.apply(this, arguments);
}
_.extend(SpacerNullField.prototype, InputField.prototype, {
    toSerialized: function () {},
    fromSerialized: function () {},
    render: function () {
        this.$parent.append("<hr>");
    }
});


var HeaderNullField = function () {
    return SpacerNullField.apply(this, arguments);
}
_.extend(HeaderNullField.prototype, SpacerNullField.prototype, {
    render: function () {
        this.$parent.append( $("<h4>").text(this.schema.label) );
    }
});


var VisualForm = function($el){
    this.$el = $el;
    this.fields = [];
    this.settings = {};
    this.initDataForm();
    this.initSettings();
    this.buildSettingsForm();
    this.getData();
    this.setupEvents();
};
_.extend(VisualForm, {
    create: function(visual_type, $el){
        var Cls
        switch (visual_type){
            case 0:
                Cls = EndpointAggregationForm;
                break;
            case 1:
                Cls = CrossviewForm;
                break;
            case 2:
                Cls = RoBHeatmapForm;
                break;
            case 3:
                Cls = RoBBarchartForm;
                break;
            default:
                throw "Error - unknown visualization-type: {0}".printf(visual_type);
        }
        return new Cls($el)
    }
});
VisualForm.prototype = {
    setupEvents: function(){
        var self = this,
            setDataChanged = function(){self.dataSynced=false;},
            $data = this.$el.find("#data"),
            $settings = this.$el.find("#settings")
            $preview = this.$el.find("#preview");

        // check if any data have changed
        $data.find(":input").on('change', setDataChanged);
        $data.on('djselectableadd djselectableremove', setDataChanged);
        $data.find('.wysihtml5-sandbox').contents().find('body').on("keyup", setDataChanged);

        // whenever data is synced, rebuild
        $settings.on('dataSynched', $.proxy(this.unpackSettings, this));
        $preview.on('dataSynched', $.proxy(this.buildPreview, this));

        $('a[data-toggle="tab"]').on('show', function(e){
            var toShow = $(e.target).attr('href'),
                shown = $(e.relatedTarget).attr('href');

            switch(shown){
                case "#data":
                    if(self.dataSynced){
                        self.unpackSettings();
                    } else {
                        self.getData();
                    }
                    break;
                case "#settings":
                    self.packSettings();
                    break;
                case "#preview":
                    self.removePreview();
                    break;
            }

            switch(toShow){
                case "#settings":
                    if(!self.dataSynced) {
                        self.addSettingsLoader();
                        self.getData();
                    }
                    break;
                case "#preview":
                    self.setPreviewLoading();
                    if(self.dataSynced){
                        $('a[data-toggle="tab"]').one('shown', $.proxy(self.buildPreview, self));
                    } else {
                        self.getData();
                    }
                    break;
            }
        });

        $('#data form').on('submit', $.proxy(this.packSettings, this));
    },
    getData: function(){
        var self = this,
            form = $('form').serialize();

        if(this.isSynching) return;
        this.dataSynced = false;
        this.isSynching = true;
        $.post(window.test_url, form, function(d){
            self.data = d;
            if (self.afterGetDataHook) self.afterGetDataHook(d);
        }).fail(function(){
            HAWCUtils.addAlert("<strong>Data request failed.</strong> Sorry, your query to return results for the visualization failed; please contact the HAWC administrator if you feel this was an error which should be fixed.");
        }).always(function(){
            self.isSynching = false;
            self.dataSynced = true;
            $('#preview, #settings').trigger('dataSynched');
        });
    },
    prepareData: function(){
        // deep-copy the data and make sure we have current settings
        var data = $.extend(true, {}, this.data);
        data.settings = $.extend(false, {}, this.settings);
        return data;
    },
    initSettings: function(){
        var settings;
        try {
            settings = JSON.parse($('#id_settings').val());
        } catch(err) {
            settings = {};
        }

        // set defaults if needed
        this.constructor.schema.forEach(function(d){
            if (d.name && settings[d.name] === undefined) settings[d.name] = d.def;
        });

        $('#id_settings').val(JSON.stringify(settings));
        this.settings = settings;
    },
    packSettings: function(){
        // settings-tab -> #id_settings serialization
        this.fields.map(function(d){ d.toSerialized(); });
        $('#id_settings').val(JSON.stringify(this.settings));
    },
    unpackSettings: function(){
        // #id_settings serialization -> settings-tab
        // must also have synced data
        this.removeSettingsLoader();
        var self = this, settings;
        try {
            settings = JSON.parse($('#id_settings').val());
            _.each(settings, function(val, key){
                if(self.settings[key]) self.settings[key] = val;
            });
        } catch(err) {}
        this.fields.forEach(function(d){ d.fromSerialized(); });
    },
    buildSettingsForm: function(){
        var $parent = this.$el.find("#settings"),
            self = this,
            getParent = function(val){
                return self.settingsTabs[val] || $parent;
            };

        this.buildSettingsSubtabs($parent);

        this.constructor.schema.forEach(function(d){
            self.fields.push(new d.type(d, getParent(d.tab), self));
        });

        self.fields.forEach(function(d){d.render();});
    },
    buildSettingsSubtabs: function($parent){
        var self = this,
            tabs = this.constructor.tabs || [],
            tablinks = [],
            ul, div, isActive;

        this.settingsTabs = {}

        if (tabs.length === 0) return;

        _.each(tabs, function(d, i){
            isActive = (i===0) ? 'active"' : "";
            self.settingsTabs[d.name] = $('<div id="settings_{0}" class="tab-pane {1}">'.printf(d.name, isActive));
            tablinks.push('<li class="{0}"><a href="#settings_{1}" data-toggle="tab">{2}</a></li>'.printf(isActive, d.name, d.label))
        });

        $('<ul class="nav nav-tabs">')
            .append(tablinks)
            .appendTo($parent);

        $('<div class="tab-content">')
            .append(_.values(self.settingsTabs))
            .appendTo($parent);
    },
    setPreviewLoading: function(){
        var $settings = (this.$el.find("#settings")),
            loading = $('<p class="loader">Loading... <img src="/static/img/loading.gif"></p>');
        $preview.html(loading);
    },
    addSettingsLoader: function(){
        var div = $('#settings'),
            self = this, loader;
        loader = div.find('p.loader');
        if(loader.length === 0) loader = $('<p class="loader">Loading... <img src="/static/img/loading.gif"></p>');
        div.children().hide(0, function(){div.append(loader).show();});
    },
    removeSettingsLoader: function(){
        var div = $('#settings');
        div.find('p.loader').remove();
        div.children().show(800);
    },
    initDataForm: function(){},
    buildPreview: HAWCUtils.abstractMethod,
    removePreview: function(){
        this.updateSettingsFromPreview();
        $("#preview").empty();
        delete this.preview;
    },
    updateSettingsFromPreview: HAWCUtils.abstractMethod
};


var EndpointAggregationForm = function($el){
    VisualForm.apply(this, arguments);
};
_.extend(EndpointAggregationForm, {
    schema: []
});
_.extend(EndpointAggregationForm.prototype, VisualForm.prototype, {
    buildPreview: function(){
        var data = this.prepareData();
        this.preview = new EndpointAggregation(data).displayAsPage( $("#preview").empty() );
    },
    updateSettingsFromPreview: function(){}
});


var CrossviewSelectorField = function () {
    return TableField.apply(this, arguments);
}
_.extend(CrossviewSelectorField.prototype, TableField.prototype, {
    renderHeader: function () {
        return $('<tr>')
            .append(
                '<th>Field name</th>',
                '<th>Values</th>',
                '<th>Number of columns</th>',
                '<th>X position</th>',
                '<th>Y position</th>',
                this.thOrdering({showNew: true})
            ).appendTo(this.$thead);
    },
    addRow: function () {
        var self = this,
            nameTd = this.addTdSelect('name', [
                    'study',
                    'experiment_type',
                    'route_of_exposure',
                    'lifestage_exposed',
                    'species',
                    'sex',
                    'generation',
                    'effects',
                    'system',
                    'organ',
                    'effect',
                ]).attr('class', 'valuesSome'),
            valuesTd = this.addTdSelectMultiple('values', []),
            values = valuesTd.find('select').attr('size', 8).css('overflow-y', 'scroll'),
            name = nameTd.find('select'),
            setValues = function(fld){
                var isLog = $('input[name="dose_isLog"]').prop('checked'),
                    opts = _.chain(CrossviewPlot.get_options(self.parent.endpoints, fld, isLog))
                            .map(function(d){return '<option value="{0}" selected>{0}</option>'.printf(d)})
                            .value();
                values.html(opts);
            }, allValues, allValuesLeg;

        allValues = $('<input name="allValues" type="checkbox" checked>').on('change', function(){
            if ($(this).prop('checked')){
                values.hide();
            } else {
                values.show();
                setValues(name.val());
            }
        }).trigger('change');

        allValuesLeg = $('<label class="checkbox">')
            .append(allValues)
            .append("Use all values")
            .prependTo(valuesTd);

        name.on('change', function(d){setValues($(this).val());});

        return $('<tr>')
            .append(
                nameTd,
                valuesTd,
                this.addTdInt('columns', 1),
                this.addTdInt('x', 0),
                this.addTdInt('y', 0),
                this.tdOrdering()
            ).appendTo(this.$tbody);
    },
    fromSerializedRow: function (d,i) {
        var row = this.addRow();
        row.find('select[name="name"]').val(d.name);
        row.find('input[name="allValues"]').prop('checked', d.allValues).trigger('change');
        row.find('select[name="values"]').val(d.values);
        row.find('input[name="columns"]').val(d.columns);
        row.find('input[name="x"]').val(d.x);
        row.find('input[name="y"]').val(d.y);
    },
    toSerializedRow: function (row) {
        row = $(row);
        return {
            "name": row.find('select[name="name"]').val(),
            "allValues": row.find('input[name="allValues"]').prop('checked'),
            "values": row.find('select[name="values"]').val(),
            "columns": parseInt(row.find('input[name="columns"]').val(), 10),
            "x": parseInt(row.find('input[name="x"]').val(), 10),
            "y": parseInt(row.find('input[name="y"]').val(), 10),
        }
    }
});


var CrossviewForm = function(){
    VisualForm.apply(this, arguments);
};
_.extend(CrossviewForm, {
    tabs: [
        {name: "overall",       label: "General settings"},
        {name: "filters",       label: "Crossview filters"},
        {name: "references",    label: "References"}
    ],
    schema: [
        {
            type: TextField,
            name: "title",
            label: "Title",
            def: "Title",
            tab: "overall"
        },
        {
            type: TextField,
            name: "xAxisLabel",
            label: "X-axis label",
            def: "Dose (<add units>)",
            tab: "overall"
        },
        {
            type: TextField,
            name: "yAxisLabel",
            label: "Y-axis label",
            def: "% change from control (continuous), % incidence (dichotomous)",
            tab: "overall"
        },
        {
            type: IntegerField,
            name: "width",
            label: "Overall width (px)",
            def: 1100,
            helpText: "Overall width, including plot and tags",
            tab: "overall"
        },
        {
            type: IntegerField,
            name: "height",
            label: "Overall height (px)",
            def: 600,
            helpText: "Overall height, including plot and tags",
            tab: "overall"
        },
        {
            type: IntegerField,
            name: "inner_width",
            label: "Plot width (px)",
            def: 940,
            tab: "overall"
        },
        {
            type: IntegerField,
            name: "inner_height",
            label: "Plot height (px)",
            def: 520,
            tab: "overall"
        },
        {
            type: IntegerField,
            name: "padding_left",
            label: "Plot padding-left (px)",
            def: 75,
            tab: "overall"
        },
        {
            type: IntegerField,
            name: "padding_top",
            label: "Plot padding-top (px)",
            def: 45,
            tab: "overall"
        },
        {
            type: CheckboxField,
            name: "dose_isLog",
            label: "Use logscale for dose",
            def: true,
            tab: "overall"
        },
        {
            type: TextField,
            name: "dose_range",
            label: "Dose-axis range",
            tab: "overall",
            helpText: 'If left blank, calculated automatically from data (ex: "1, 100").'
        },
        {
            type: TextField,
            name: "response_range",
            label: "Response-axis range",
            tab: "overall",
            helpText: 'If left blank, calculated automatically from data (ex: "-0.5, 2.5").'
        },
        {
            type: CrossviewSelectorField,
            prependSpacer: false,
            name: "filters",
            colWidths: [24, 25, 12, 12, 12, 15],
            tab: "filters"
        },
        {
            type: ReferenceLineField,
            prependSpacer: false,
            label: "Dose reference line",
            name: "reflines_dose",
            colWidths: [20, 40, 20, 20],
            tab: "references"
        },
        {
            type: ReferenceRangeField,
            prependSpacer: true,
            label: "Dose reference range",
            name: "refranges_dose",
            colWidths: [10, 10, 40, 20, 20],
            tab: "references"
        },
        {
            type: ReferenceLineField,
            prependSpacer: true,
            label: "Response reference line",
            name: "reflines_response",
            colWidths: [20, 40, 20, 20],
            tab: "references"
        },
        {
            type: ReferenceRangeField,
            prependSpacer: true,
            label: "Response reference range",
            name: "refranges_response",
            colWidths: [10, 10, 40, 20, 20],
            tab: "references"
        },
        {
            type: ReferenceLabelField,
            prependSpacer: true,
            label: "Figure captions",
            name: "labels",
            colWidths: [50, 20, 10, 10, 10],
            tab: "references"
        },
    ]
});
_.extend(CrossviewForm.prototype, VisualForm.prototype, {
    buildPreview: function(){
        var data = this.prepareData();
        this.preview = new Crossview(data);
        this.preview.displayAsPage( $("#preview").empty(), {"dev": true});
    },
    updateSettingsFromPreview: function(){
        settings = $('#id_settings').val(JSON.stringify(this.preview.data.settings));
        this.unpackSettings();
    },
    afterGetDataHook: function(data){
        var endpoints = data.endpoints.map(function(d){
            var e = new Endpoint(d);
            e.switch_dose_units(data.dose_units);
            return e;
        });
        this.endpoints = endpoints;
    },
    initDataForm: function(){
        $('#id_prefilter_system').on('change', function(){
            var sys = $('#id_systems').parent().parent();
            ($(this).prop('checked')) ? sys.show(1000) : sys.hide(0);
        }).trigger('change');

        $('#id_prefilter_effect').on('change', function(){
            var sys = $('#id_effects').parent().parent();
            ($(this).prop('checked')) ? sys.show(1000) : sys.hide(0);
        }).trigger('change');
    }
});


var RoBHeatmapForm = function($el){
    VisualForm.apply(this, arguments);
};
_.extend(RoBHeatmapForm, {
    schema: [
        {
            type: TextField,
            name: "title",
            label: "Title",
            def: ""
        },
        {
            type: TextField,
            name: "xAxisLabel",
            label: "X-axis label",
            def: ""
        },
        {
            type: TextField,
            name: "yAxisLabel",
            label: "Y-axis label",
            def: ""
        },
        {
            type: IntegerField,
            name: "padding_top",
            label: "Plot padding-top (px)",
            def: 20
        },
        {
            type: IntegerField,
            name: "cell_size",
            label: "Cell-size (px)",
            def: 40
        },
        {
            type: IntegerField,
            name: "padding_right",
            label: "Plot padding-right (px)",
            def: 10
        },
        {
            type: IntegerField,
            name: "padding_bottom",
            label: "Plot padding-bottom (px)",
            def: 35
        },
        {
            type: IntegerField,
            name: "padding_left",
            label: "Plot padding-left (px)",
            def: 20
        },
        {
            type: SelectField,
            name: "x_field",
            label: "X-axis field",
            opts: [
                ["study", "Study"],
                ["metric", "RoB metric"]
            ],
            def: "metric"
        }
    ]
});
_.extend(RoBHeatmapForm.prototype, VisualForm.prototype, {
    buildPreview: function(){
        var data = this.prepareData();
        this.preview = new RoBHeatmap(data).displayAsPage( $("#preview").empty() );
    },
    initDataForm: function(){
        var showHideDiv = function(shouldShow, $el){
            (shouldShow) ? $el.show(1000) : $el.hide(0);
        }, updateStudies = function(){
            var shouldHide = (
                $("#id_prefilter_system").prop('checked') ||
                $("#id_prefilter_effect").prop('checked'));
            showHideDiv(!shouldHide, $('#div_id_studies'));
            if(shouldHide) $('#id_studies option').prop('selected', false);
        };

        $('#id_prefilter_system').on('change', function(){
            var showOpts = $(this).prop('checked');
            showHideDiv(showOpts, $('#div_id_systems'));
            updateStudies();
        }).trigger('change');

        $('#id_prefilter_effect').on('change', function(){
            var showOpts = $(this).prop('checked');
            showHideDiv(showOpts, $('#div_id_effects'));
            updateStudies();
        }).trigger('change');
    },
    updateSettingsFromPreview: function(){}
});


var RoBBarchartForm = function($el){
    VisualForm.apply(this, arguments);
};
_.extend(RoBBarchartForm, {
    schema: [
        {
            type: TextField,
            name: "title",
            label: "Title",
            def: "Title"
        },
        {
            type: TextField,
            name: "xAxisLabel",
            label: "X-axis label",
            def: "Percent of studies"
        },
        {
            type: TextField,
            name: "yAxisLabel",
            label: "Y-axis label",
            def: ""
        },
        {
            type: IntegerField,
            name: "plot_width",
            label: "Plot width (px)",
            def: 400
        },
        {
            type: IntegerField,
            name: "row_height",
            label: "Row height (px)",
            def: 30
        },
        {
            type: IntegerField,
            name: "padding_top",
            label: "Plot padding-top (px)",
            def: 40
        },
        {
            type: IntegerField,
            name: "padding_right",
            label: "Plot padding-right (px)",
            def: 25
        },
        {
            type: IntegerField,
            name: "padding_bottom",
            label: "Plot padding-bottom (px)",
            def: 40
        },
        {
            type: IntegerField,
            name: "padding_left",
            label: "Plot padding-left (px)",
            def: 25
        },
        {
            type: CheckboxField,
            name: "show_values",
            label: "Show values on plot",
            def: true
        }
    ]
});
_.extend(RoBBarchartForm.prototype, VisualForm.prototype, RoBHeatmapForm.prototype, {
    buildPreview: function(){
        var data = this.prepareData();
        this.preview = new RoBBarchart(data).displayAsPage( $("#preview").empty() );
    }
});
