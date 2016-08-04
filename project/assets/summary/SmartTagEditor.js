class SmartTagEditor {

    constructor($el, options){
        options = options || {};
        this.$el = $el;
        this.init();

        if (options.submitEl){
            var self = this;
            $(options.submitEl).submit(function(){
                self.prepareSubmission();
                return true;
            });
        }
    }

    init(){

        this.$el
            .css('height', '300px')
            .wysihtml5({
                'smartTag': true,
                'smartTagModal': '#smartTagModal',
                'font-styles': false,
                'stylesheets': [
                    '//cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/2.2.2/css/bootstrap.min.css',
                    '//cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/2.2.2/css/bootstrap-responsive.min.css',
                    '/static/css/hawc.css',
                    '/static/css/d3.css',
                ],
            });

        var editor = this.$el.data('wysihtml5').editor;
        editor.on('load', function(){
            SmartTag.initialize_tags($(editor.composer.doc));
        });
        this.editor = editor;
    }

    prepareSubmission(){
        InlineRendering.reset_renderings($(this.editor.composer.doc));
        this.editor.synchronizer.sync();
    }

    setContent(content){
        this.editor.setValue(content);
        SmartTag.initialize_tags($(this.editor.composer.element));
    }

}

export default SmartTagEditor;
