import $ from '$';
import Quill from 'QuillUno';

import SmartTag from './QuillSmartTag';
import SmartInline from './QuillSmartInline';


Quill.register(SmartTag, true);
Quill.register(SmartInline, true);


const toolbarOptions = {
        container: [
            [
                {header: [false, 1, 2, 3, 4]},
            ],
            [
                'bold',
                'italic',
                'underline',
                'strike',
            ],
            [
                {script: 'sub'},
                {script: 'super'},
            ],
            [
                {color: []},
                {background:[]},
            ],
            [
                'link',
                {list: 'ordered'},
                {list: 'bullet' },
                'blockquote',
            ],
            [
                'smartTag', 'smartInline',
            ],
            [
                'clean',
            ],
        ],
        handlers: {
            smartTag(value){
                let sel = this.quill.getSelection();
                if (sel === null || sel.length === 0){
                    return;
                }
                this.quill.format('smartTag', value);
            },
            smartInline(value){
                let sel = this.quill.getSelection();
                if (sel === null || sel.length === 0){
                    return;
                }
                this.quill.format('smartInline', value);
            },
        },
    },
    formatToolbarExtras = function(q){
        var tb = q.getModule('toolbar');
        $(tb.container).find('.ql-smartTag')
            .append('<i class="fa fa-tag">');
        $(tb.container).find('.ql-smartInline')
            .append('<i class="fa fa-sticky-note">');
    };

export default function(){
    return this.each(function(){
        let editor = document.createElement('div'),
            textarea = $(this),
            q;

        textarea.hide().before(editor);
        q = new Quill(editor, {
            modules: {
                toolbar: toolbarOptions,
            },
            theme: 'snow',
        });

        formatToolbarExtras(q);
        q.pasteHTML(textarea.val());
        q.on('text-change', function(delta, oldDelta, source){
            let content = $(editor).find('.ql-editor').html();
            textarea.val(content);
        });
        textarea.data('_quill', q);
    });
}
