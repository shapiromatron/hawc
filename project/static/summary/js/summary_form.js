VisualForm = function($el){
    this.$el = $el;
    this.setup_events();
    this.get_data();
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
    setup_events: function(){

        var self = this,
            dataChanged = false,
            settingsChanged = false,
            setDataChanged = function(){dataChanged=true;},
            setSettingsChanged = function(){settingsChanged=true;},
            $data = (this.$el.find("#data")),
            $settings = (this.$el.find("#settings"))
            $preview = (this.$el.find("#preview"));

        // check if any data have changed
        $data.find(":input").on('change', setDataChanged);
        $data.on('djselectableadd djselectableremove', setDataChanged);
        $data.find('.wysihtml5-sandbox').contents().find('body').on("keyup", setDataChanged);

        $data.find("#id_settings").on('change', setSettingsChanged);
        $settings.find(":input").on('change', setSettingsChanged);

        // check if any settings have changed
        $('a[data-toggle="tab"]').on('show', function(e){
            var showing = $(e.target).attr('href'),
                shown = $(e.relatedTarget).attr('href');

            if(shown === "#data"){
                if(dataChanged) self.get_data();
                dataChanged = false;
            }
            if(shown==="#data" && showing==="#settings"){
                if(settingsChanged) self.unpack_settings();
                settingsChanged = false;

            }
            if(shown==="#settings" && showing==="#data"){
                if(settingsChanged) self.pack_settings();
                settingsChanged = false;
            }
        });

        $('#data form').on('submit', $.proxy(this.pack_settings, this));
    },
    get_data: function(){
        var data = this.pack_data()
            self = this;
        $.post(window.test_url, data, function(d){
            console.log(d);
            self.data = d;
        }).fail(function(){
            console.log('failed');
        });
    },
    pack_data: function(){
        throw "Abstract method; requires implementation";
    },
    pack_settings: function(){
        throw "Abstract method; requires implementation";
    },
    unpack_settings: function(){
        throw "Abstract method; requires implementation";
    }
};


EndpointAggregationForm = function($el){
    VisualForm.apply(this, arguments);
}
_.extend(EndpointAggregationForm.prototype, VisualForm.prototype, {
    pack_data: function(){
        console.log('got data');
    },
    pack_settings: function(){
        console.log('packed settings');
    },
    unpack_settings: function(){
        console.log('unpacked settings');
    }
});


CrossviewForm = function(){
    VisualForm.apply(this, arguments);
}
_.extend(CrossviewForm.prototype, VisualForm.prototype, {
    pack_data: function(){
        console.log('got data');
    },
    pack_settings: function(){
        console.log('packed settings');
    },
    unpack_settings: function(){
        console.log('unpacked settings');
    }
});


