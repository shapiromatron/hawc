import Quill from 'QuillUno';


let Inline = Quill.imports['blots/inline'];

class SmartTag extends Inline {
    static create(value) {
        let el = document.createElement('SPAN');
        el.setAttribute('class', 'smart-tag active');
        el.dataset.id = value.id;
        el.dataset.type = value.type;
        return el;
    }

    static formats(domNode) {
        return {
            id: parseInt(domNode.dataset.id),
            type: domNode.dataset.type,
        };
    }
}
SmartTag.blotName = 'smartTag';
SmartTag.tagName = 'SPAN';

export default SmartTag;
