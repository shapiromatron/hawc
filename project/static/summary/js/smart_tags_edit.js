(function(wysihtml5, jQuery, SmartTag) {
    var dom = wysihtml5.dom;
    wysihtml5.commands.createSmartTag = {
        exec: function(composer, command, values) {
            var doc = composer.doc,
                anchor,
                node_name,
                textContent,
                textNode;

            if (values.display_type === "click"){
                node_name = "SPAN";
                textContent = values['title'];
            } else {
                node_name = "DIV";
                textContent = values['caption'];
            }

            // create element
            anchor = doc.createElement(node_name);
            dom.setTextContent(anchor, textContent);
            anchor.setAttribute("data-type", values["data-type"]);
            anchor.setAttribute("data-pk", values["data-pk"]);
            anchor.setAttribute("class", "smart-tag active");

            // clear existing
            if(values.existing){
                composer.selection.selectNode(values.existing);
                values.existing.remove();
            }

            // insert new element
            if (node_name === "SPAN"){
                textNode = doc.createTextNode(wysihtml5.INVISIBLE_SPACE);
                composer.selection.insertNode(textNode);
                composer.selection.setBefore(textNode);
                composer.selection.insertNode(anchor);
                composer.selection.setAfter(textNode);
            } else {
                composer.selection.insertNode(anchor);
            }

            SmartTag.initialize_tags($(composer.doc));
        }
    };
})(wysihtml5, jQuery, SmartTag);


SmartTagSearch = function(editor, $modal){
    var self = this,
        input_resource_type = $modal.find('.resource-type'),
        input_unique_pk = $modal.find('.unique-pk'),
        input_search = $modal.find('.search'),
        input_title = $modal.find('.smart-tag-title'),
        input_caption = $modal.find('.smart-tag-caption'),
        input_display_type = $modal.find('.display_type');

    this.$results_div = $modal.find('.search_results');

    var search = function(){
        var val = input_search.val(),
            resource = input_resource_type.find('option:selected').val();

        if(val.length<3){
            self._set_results([]);
            return;
        }

        self._set_results(['<p>Searching for {0} titled "{1}"... <img src="/static/img/loading.gif"></p>'
                          .printf(input_resource_type.find('option:selected').text(), val)]);

        switch (resource){
            case "endpoint":
                self._endpoint_search(val);
                break;
            case "study":
                self._study_search(val);
                break;
            case "aggregation":
                self._aggregation_search(val);
                break;
            case "data_pivot":
                self._dp_search(val);
                break;
            default:
                self._set_results(['<p>Unknown resource type.</p>']);
        }
    };

    var reset_form = function(){
        self.$results_div.empty();
        input_search.val("");
        input_title.val("");
        input_caption.val("");
    };

    var show_display_settings = function(bool){
        // toggle between resource and display settings
        var values = {true: "inline", false: "none"};
        $modal.find('.resource_options').css("display", values[!bool]);
        $modal.find('.change_resource').css("display", values[bool]);
        $modal.find('.resource_settings').css("display", values[bool]);
        $modal.find('.display_options').css("display", values[bool]);
    };

    var show_inline_settings = function(bool){
        // toggle between inline and click settings
        var values = {true: "block", false: "none"};
        $modal.find('.click_options').css("display", values[!bool]);
        $modal.find('.inline_options').css("display", values[bool]);
    };

    var set_fixed_resource = function(resource_type, name){
        $modal.find('.resource_type_value').html(resource_type);
        $modal.find('.resource_name').html(name);
    };

    var load_smarttag_span = function($span){
        input_unique_pk.val($span.data('pk'));
        input_resource_type
            .find('option[value="{0}"]'.printf($span.data('type')))
            .prop('selected', true);
        input_search.val($span.text());
        input_title.val($span.text());
        input_display_type.find('option[value="click"]').prop('selected', true);
        set_fixed_resource(input_resource_type.find('option:selected').text(), $span.text());
        show_display_settings(true);
        show_inline_settings(false);
    };

    var load_smarttag_div = function($div){
        var type = $div.data('d').smart_tag.$tag.data('type'),
            name = $div.data('d').smart_tag.resource.get_name();
        input_unique_pk.val($div.data('d').smart_tag.$tag.data('pk'));
        input_resource_type
            .find('option[value="{0}"]'.printf(type))
            .prop('selected', true);
        input_search.val(name);
        input_display_type
            .find('option[value="inline"]')
            .prop('selected', true);
        input_caption.val($div.find('.caption').html());
        set_fixed_resource(input_resource_type.find('option:selected').text(), name);
        show_display_settings(true);
        show_inline_settings(true);
    };

    var configure_startup = function(){
        reset_form();
        show_display_settings(false);
        show_inline_settings(false);

        var anchor = $(editor.composer.selection.getSelection().anchorNode);
        var smart_tags = anchor.parents('.smart-tag'),
            smart_divs = anchor.parents('.inline-smart-tag-container');
        if(smart_tags.length>0) load_smarttag_span($(smart_tags[0]));
        if(smart_divs.length>0) load_smarttag_div($(smart_divs[0]));
    };

    input_search.on('keyup', search);

    $modal.on('change', '.display_type', function(){
        var val = $(this).find('option:selected').val();
        show_inline_settings(val === "inline");
    });

    this.$results_div.on('click', '.smart-tag-results', function(e){
        e.preventDefault();
        var data = $(this).data();
        input_unique_pk.val(data.pk);
        input_title.val(data.name);
        input_caption.val(data.caption);
        set_fixed_resource(input_resource_type.find('option:selected').text(),
                           data.name);
        show_display_settings(true);
    });

    $modal.on('click', '.change_resource', function(){
        show_display_settings(false);
    });

    $modal.on('show', configure_startup);
};

SmartTagSearch.prototype._set_results = function(content){
    this.$results_div.html(content);
};

SmartTagSearch.prototype._endpoint_search = function(search_string){
    var self = this,
        data = {'endpoint_name': search_string};

    $.get('/ani/assessment/{0}/endpoints/search/q/'.printf(window.assessment_pk), data, function(d){
        var content = [];
        if(d.status !== "ok" || d.endpoints.length === 0){
            content.push("<p>No results found.</p>");
        } else {
            d.endpoints.forEach(function(e_data){
                var add_button = '  <a class="btn btn-mini smart-tag-results"><i class="icon-plus"></i></a> <br>',
                    endpoint = new Endpoint(e_data),
                    smart_data = {"pk": endpoint.data.pk,
                                  "name": endpoint.data.name,
                                  "caption": ""};

                content.push($(endpoint.build_breadcrumbs() + add_button)
                                .data(smart_data));
            });
        }
        self._set_results(content);
    });
};

SmartTagSearch.prototype._study_search = function(search_string){
    var self = this,
        data = {'short_citation': search_string};

    $.post('/study/assessment/{0}/search/'.printf(window.assessment_pk), data, function(d){
        var content = [];
        if(d.status !== "success" || d.studies.length === 0){
            content.push("<p>No results found.</p>");
        } else {
            d.studies.forEach(function(study_data){
                var add_button = '  <a class="btn btn-mini smart-tag-results"><i class="icon-plus"></i></a> <br>',
                    study = new Study(study_data),
                    smart_data = {"pk": study.data.pk,
                                  "name": study.data.short_citation,
                                  "caption": ""};

                content.push($(study.build_breadcrumbs() + add_button)
                                .data(smart_data));
            });
        }
        self._set_results(content);
    });
};

SmartTagSearch.prototype._aggregation_search = function(search_string){
    var self = this,
        data = {'name': search_string};

    $.post('/ani/{0}/aggregation/search/'.printf(window.assessment_pk), data, function(d){
        var content = [];
        if(d.status !== "success" || d.aggregations.length === 0){
            content.push("<p>No results found.</p>");
        } else {
            d.aggregations.forEach(function(agg_data){
                var add_button = '  <a class="btn btn-mini smart-tag-results"><i class="icon-plus"></i></a> <br>',
                    agg = new Aggregation(agg_data.endpoints, agg_data.name),
                    smart_data = {"pk": agg_data.pk,
                                  "name": agg_data.name,
                                  "caption": ""};
                var breadcrumb = '<a target="_blank" href="{0}">{1}</a>'
                                    .printf(agg_data.url, agg_data.name);
                content.push($(breadcrumb + add_button).data(smart_data));
            });
        }
        self._set_results(content);
    });
};

SmartTagSearch.prototype._dp_search = function(search_string){
    var self = this,
        data = {'title': search_string};

    $.post('/summary/data-pivot/assessment/{0}/search/json/'.printf(window.assessment_pk), data, function(d){
        var content = [];
        if(d.status !== "success" || d.dps.length === 0){
            content.push("<p>No results found.</p>");
        } else {
            d.dps.forEach(function(dp){
                var add_button = '  <a class="btn btn-mini smart-tag-results"><i class="icon-plus"></i></a> <br>',
                    smart_data = {"pk": dp.pk,
                                  "name": dp.title,
                                  "caption": dp.caption};
                var breadcrumb = '<a target="_blank" href="{0}">{1}</a>'
                                    .printf(dp.url, dp.title);
                content.push($(breadcrumb + add_button).data(smart_data));
            });
        }
        self._set_results(content);
    });
};
