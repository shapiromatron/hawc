import Quill from 'QuillUno';


let Block = Quill.imports['blots/block'];

class SmartInline extends Block {
    static create(value) {
        let el = document.createElement('DIV');
        el.setAttribute('class', 'inlineSmartTagContainer');
        el.dataset.id = 123;
        el.dataset.type = 'Endpoint';
        return el;
    }

    static formats(domNode) {
        return 'smartInline';
    }
}
SmartInline.blotName = 'smartInline';
SmartInline.tagName = 'DIV';

export default SmartInline;
