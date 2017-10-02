import $ from '$';

import HAWCUtils from 'utils/HAWCUtils';


class BaseVisual {

    constructor(data){
        this.data = data;
        this.data.created = new Date(this.data.created);
        this.data.last_updated = new Date(this.data.last_updated);
    }

    build_row(opts){
        let arr = [
            '<a href="{0}">{1}</a>'.printf(this.data.url, this.data.title),
            this.data.visual_type,
            HAWCUtils.truncateChars(this.data.caption),
            this.data.created.toString(),
            this.data.last_updated.toString(),
        ];
        if (opts.showPublished){
            arr.splice(3, 0, HAWCUtils.booleanCheckbox(this.data.published));
        }
        return arr;
    }

    displayAsPage($el, options){
        throw 'Abstract method; requires implementation';
    }

    displayAsModal($el, options){
        throw 'Abstract method; requires implementation';
    }

    addActionsMenu(){
        return HAWCUtils.pageActionsButton([
            'Visualization editing',
            {url: this.data.url_update, text: 'Update'},
            {url: this.data.url_delete, text: 'Delete'},
        ]);
    }

    object_hyperlink(){
        return $('<a>')
            .attr('href', this.data.url)
            .attr('target', '_blank')
            .text(this.data.title);
    }

}

export default BaseVisual;
