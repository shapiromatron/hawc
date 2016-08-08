import $ from '$';


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
    }

    prepareSubmission(){
        // TODO: trigger smart-tag deconstruction
    }

    setContent(content){
        let q = this.$el.data('_quill');
        q.pasteHTML(content);
        // TODO: trigger smart-tag construction
    }

}

export default SmartTagEditor;
