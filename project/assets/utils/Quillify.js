import $ from '$';
import Quill from 'quill';

import 'quill/dist/quill.snow.css';

import SmartTag from 'smartTags/QuillSmartTag';
import SmartInline from 'smartTags/QuillSmartInline';
import SmartTagModal from 'smartTags/QuillSmartTagModal';
import SmartTagContainer from 'smartTags/SmartTagContainer';


Quill.register(SmartTag, true);
Quill.register(SmartInline, true);

const toolbarOptions = {
        container: [
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
                    window.alert('Select text to add a smart-tag.');
                    return;
                }
                this.quill.smartTagModal.showModal('smartTag', sel, value);
            },
            smartInline(value){
                let sel = this.quill.getSelection();
                if (sel === null || sel.length === 0){
                    window.alert('Select text to add an inline smart-tag.');
                    return;
                }
                this.quill.smartTagModal.showModal('smartInline', sel, value);
            },
        },
    },
    formatSmartTagButtons = function(q){
        var tb = q.getModule('toolbar');
        $(tb.container).find('.ql-smartTag')
            .append('<i class="fa fa-tag">');
        $(tb.container).find('.ql-smartInline')
            .append('<i class="fa fa-sticky-note">');
        q.smartTagModal = new SmartTagModal(q, $('#smartTagModal'));
    },
    hideSmartTagButtons = function(q){
        var tb = q.getModule('toolbar');
        $(tb.container).find('.ql-smartTag').hide();
        $(tb.container).find('.ql-smartInline').hide();
    };

export default function(){

    let modal = $('#smartTagModal'),
        showHawcTools = (modal.length === 1);

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

        if (showHawcTools){
            q.stc = new SmartTagContainer($(q.container).find('.ql-editor'));
            formatSmartTagButtons(q);
        } else {
            hideSmartTagButtons(q);
        }

        q.pasteHTML(textarea.val());
        q.on('text-change', function(delta, oldDelta, source){
            let content = $(editor).find('.ql-editor').html();
            textarea.val(content);
        });
        textarea.data('_quill', q);

        if (q.stc){
            q.stc.enableModals();
        }
    });
}
