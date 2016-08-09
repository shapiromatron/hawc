import Quill from 'QuillUno';


let Block = Quill.imports['blots/block'];

class SmartInline extends Block {
    static create(value) {
        let el = document.createElement('DIV');
        el.setAttribute('class', 'inlineSmartTagContainer');
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
SmartInline.blotName = 'smartInline';
SmartInline.tagName = 'DIV';

export default SmartInline;
