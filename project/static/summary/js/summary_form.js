var InputField = function(schema, $parent, parent){
    this.$parent = $parent;
    this.schema = schema;
    this.parent = parent;
    return this;
};
_.extend(InputField.prototype, {
    toSerialized: function () {
        throw "Abstract method; requires implementation";
    },
    fromSerialized: function () {
        throw "Abstract method; requires implementation";
    },
    render: function () {
        throw "Abstract method; requires implementation";
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
            default:
                throw "Error - unknown visualization-type: {0}".printf(visual_type);
        }
        return new Cls($el)
    }
});
VisualForm.prototype = {
    setupEvents: function(){

        var self = this,
            dataChanged = false,
            setDataChanged = function(){dataChanged=true;},
            $data = this.$el.find("#data"),
            $settings = this.$el.find("#settings")
            $preview = this.$el.find("#preview");

        // check if any data have changed
        $data.find(":input").on('change', setDataChanged);
        $data.on('djselectableadd djselectableremove', setDataChanged);
        $data.find('.wysihtml5-sandbox').contents().find('body').on("keyup", setDataChanged);

        $('a[data-toggle="tab"]').on('show', function(e){
            var toShow = $(e.target).attr('href'),
                shown = $(e.relatedTarget).attr('href');

            if(shown==="#settings") self.packSettings();

            if(shown==="#data") self.unpackSettings();

            if(shown==="#preview") self.removePreview();

            if(toShow==="#preview"){
                self.setPreviewLoading();
                if(dataChanged){
                    self.getData(self.buildPreview)
                    dataChanged = false;
                } else {
                    $('a[data-toggle="tab"]').one('shown', $.proxy(self.buildPreview, self));
                }
            }
        });

        $('#data form').on('submit', $.proxy(this.packSettings, this));
    },
    getData: function(cb){
        var data = $('form').serialize(),
            self = this,
            $preview = this.$el.find("#preview");

        $.post(window.test_url, data)
            .success(function(d){
                self.data = d;
                if (cb) cb.apply(self);
            }).fail(function(){
                HAWCUtils.addAlert("<strong>Data request failed.</strong> Sorry, your query to return results for the visualization failed; please contact the HAWC administrator if you feel this was an error which should be fixed.");
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
            if (d.name && !settings[d.name]) settings[d.name] = d.def;
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
            self = this;

        this.constructor.schema.forEach(function(d){
            self.fields.push(new d.type(d, $parent, self));
        });

        self.fields.forEach(function(d){d.render();});
    },
    setPreviewLoading: function(){
        var $settings = (this.$el.find("#settings")),
            loading = '<p>Loading... <img src="/static/img/loading.gif"></p>';
        $preview.html(loading);
    },
    buildPreview: function(){
        throw "Abstract method; requires implementation";
    },
    removePreview: function(){
        $("#preview").empty();
        delete this.preview;
    }
};


var EndpointAggregationForm = function($el){
    VisualForm.apply(this, arguments);
};
_.extend(EndpointAggregationForm, {
    schema: [
        {
            type: TextField,
            name: "title",
            label: "Title",
            def: "Title",
            helpText: "Enter a title for the visualization, or leave blank"
        },
        {
            type: SelectField,
            name: "opts",
            label: "Title",
            def: 456,
            opts: [[123, "label"], [456, "label2"]],
            helpText: "Enter a title for the visualization, or leave blank"
        }
    ]
});
_.extend(EndpointAggregationForm.prototype, VisualForm.prototype, {
    buildPreview: function(){
        var data = this.prepareData();
        this.preview = new EndpointAggregation(data).displayAsPage( $("#preview").empty() );
    }
});


var CrossviewForm = function(){
    VisualForm.apply(this, arguments);
};
_.extend(CrossviewForm, {
    schema: [
        {
            type: HeaderNullField,
            label: "Overall plot-settings"
        },
        {
            type: TextField,
            name: "title",
            label: "Title",
            def: "Title"
        },
        {
            type: IntegerField,
            name: "width",
            label: "Overall width (px)",
            def: 1100,
            helpText: "Overall width, including plot and tags"
        },
        {
            type: IntegerField,
            name: "height",
            label: "Overall height (px)",
            def: 600,
            helpText: "Overall height, including plot and tags"
        },
        {
            type: SpacerNullField,
        },
        {
            type: HeaderNullField,
            label: "Crossview visualization-settings"
        },
        {
            type: IntegerField,
            name: "inner_width",
            label: "Plot width (px)",
            def: 940
        },
        {
            type: IntegerField,
            name: "inner_height",
            label: "Plot height (px)",
            def: 520
        },
        {
            type: IntegerField,
            name: "padding_left",
            label: "Plot padding-left (px)",
            def: 75
        },
        {
            type: IntegerField,
            name: "padding_top",
            label: "Plot padding-top (px)",
            def: 45
        },
        {
            type: SpacerNullField,
        }
    ]
});
_.extend(CrossviewForm.prototype, VisualForm.prototype, {
    buildPreview: function(){
        var data = this.prepareData();
        this.preview = new Crossview(data).displayAsPage( $("#preview").empty() );
    }
});
