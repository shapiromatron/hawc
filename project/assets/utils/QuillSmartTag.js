import Quill from 'QuillUno';


let Inline = Quill.imports['blots/inline'];

class SmartTag extends Inline {
    static create(value) {
        let el = document.createElement('SPAN');
        el.setAttribute('class', 'smart-tag active');
        el.dataset.id = 123;
        el.dataset.type = 'Endpoint';
        return el;
    }

    static formats(domNode) {
        return 'smartTag';
    }
}
SmartTag.blotName = 'smartTag';
SmartTag.tagName = 'SPAN';

export default SmartTag;
