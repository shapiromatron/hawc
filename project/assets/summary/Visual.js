class Visual {

    constructor(data){
        this.data = data;
        this.data.created = new Date(this.data.created);
        this.data.last_updated = new Date(this.data.last_updated);
    }

    static get_object(id, cb){
        $.get('/summary/api/visual/{0}/'.printf(id), function(d){
            var Cls;
            switch (d.visual_type){
            case 'animal bioassay endpoint aggregation':
                Cls = EndpointAggregation;
                break;
            case 'animal bioassay endpoint crossview':
                Cls = Crossview;
                break;
            case 'risk of bias heatmap':
                Cls = RoBHeatmap;
                break;
            case 'risk of bias barchart':
                Cls = RoBBarchart;
                break;
            default:
                throw 'Error - unknown visualization-type: {0}'.printf(d.visual_type);
            }
            cb(new Cls(d));
        });
    }

    static displayAsPage(id, $el){
        $el.html('<p>Loading... <img src="/static/img/loading.gif"></p>');
        Visual.get_object(id, function(d){d.displayAsPage($el);});
    }

    static displayAsModal(id, options){
        Visual.get_object(id, function(d){d.displayAsModal(options);});
    }

    build_row(){
        return [
            '<a href="{0}">{1}</a>'.printf(this.data.url, this.data.title),
            this.data.visual_type,
            HAWCUtils.truncateChars(this.data.caption),
            this.data.created.toString(),
            this.data.last_updated.toString(),
        ];
    }

    displayAsPage($el, options){
        throw 'Abstract method; requires implementation';
    }

    displayAsModal($el, options){
        throw 'Abstract method; requires implementation';
    }

    addActionsMenu(){
        return HAWCUtils.pageActionsButton([
            'Visualization editing',
            {url: this.data.url_update, text: 'Update'},
            {url: this.data.url_delete, text: 'Delete'},
        ]);
    }

    object_hyperlink(){
        return $('<a>')
            .attr('href', this.data.url)
            .attr('target', '_blank')
            .text(this.data.title);
    }

}

export default Visual;



