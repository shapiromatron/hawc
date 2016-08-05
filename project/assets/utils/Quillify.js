import $ from '$';
import Quill from 'QuillUno';

export default function(){

    let editor = document.createElement('div'),
        textarea = $(this),
        q;

    textarea.hide().before(editor);
    q = new Quill(editor, {theme: 'snow'});
    q.pasteHTML(textarea.val());
    q.on('text-change', function(delta, oldDelta, source){
        let content = $(editor).find('.ql-editor').html();
        textarea.val(content);
    });
}
