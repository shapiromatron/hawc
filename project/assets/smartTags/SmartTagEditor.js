import $ from '$';

import InlineRendering from './InlineRendering';
import SmartTag from './SmartTag';


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
            .quillify();

        // TODO - fix!
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
