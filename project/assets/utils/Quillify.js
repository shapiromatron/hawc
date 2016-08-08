import $ from '$';
import Quill from 'QuillUno';


let toolbarOptions = [
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
        'clean',
    ],
];


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
        q.pasteHTML(textarea.val());
        q.on('text-change', function(delta, oldDelta, source){
            let content = $(editor).find('.ql-editor').html();
            textarea.val(content);
        });
        textarea.data('_quill', q);
    });
}
