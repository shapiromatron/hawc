import $ from '$';

import DataPivot from 'dataPivot/DataPivot';
import Endpoint from 'animal/Endpoint';
import Study from 'study/Study';

import InlineRendering from './InlineRendering';
import Visual from './Visual';


class SmartTag {

    constructor(tag){
        this.$tag = $(tag).data('obj', this);
        this.type = this.$tag.data('type');
        this.pk = this.$tag.data('pk');
        this.resource = undefined;
        this.rendering = this.$tag.is('span') ? 'tooltip' : 'inline';
        if (this.rendering === 'tooltip'){
            this.$tag.on('click', $.proxy(this.display_modal, this));
        } else {
            this.display_inline();
        }
    }

    static toggle_disabled(e){
        e.preventDefault();
        $('span.smart-tag').toggleClass('active');
    }

    static initialize_tags($frame){
        var doc = $frame || $(document);

        doc.find('span.smart-tag')
            .each(function(i, v){ if(!$(this).data('obj')){new SmartTag(v);}})
            .addClass('active');

        doc.find('div.smart-tag')
            .each(function(i, v){if(!$(this).data('obj')){new SmartTag(v);}});
    }

    static getExistingTag($node){
        // if the node is an existing Tag; return the $node; else return none.
        var smart_tags = $node.parents('.smart-tag'),
            smart_divs = $node.parents('.inlineSmartTagContainer');

        if(smart_tags.length>0) return smart_tags[0];
        if(smart_divs.length>0){
            // reset inline representation to basic div caption
            var inline = $(smart_divs[0]).data('obj');
            inline.reset_rendering();
            return inline.data.$tag[0];
        }
        return null;
    }

    display_inline(){
        var context = SmartTag.context[this.type],
            cb;

        if (context === undefined){
            console.log('unknown context: {0}'.printf(this.type));
        } else {
            cb = $.proxy(
                function(obj){new InlineRendering(this)[context.inline_func](obj);},
                this);
            context.Cls.get_object(this.pk, cb);
        }
    }

    display_modal(e){
        if(!$(e.target).hasClass('active')) return;
        SmartTag.context[this.type].Cls.displayAsModal(this.pk);
    }

}

SmartTag.context = {
    endpoint: {
        Cls: Endpoint,
        inline_func: 'display_endpoint',
    },
    study: {
        Cls: Study,
        inline_func: 'display_study',
    },
    visual: {
        Cls: Visual,
        inline_func: 'display_visual',
    },
    data_pivot: {
        Cls: DataPivot,
        inline_func: 'display_data_pivot',
    },
};

export default SmartTag;
