import $ from '$';
import _ from 'lodash';


class HAWCModal {

    constructor(){
        // singleton modal instance
        var $modalDiv = $('#hawcModal');
        if ($modalDiv.length === 0){
            $modalDiv = $('<div id="hawcModal" class="modal hide fade" tabindex="-1" role="dialog" data-backdrop="static"></div>')
                .append('<div class="modal-header"></div>')
                .append('<div class="modal-body"></div>')
                .append('<div class="modal-footer"></div>')
                .appendTo($('body'));
            $(window).on('resize', this._resizeModal.bind(this));
        }
        this.$modalDiv = $modalDiv;
    }

    show(options, cb){
        this.fixedSize = options && options.fixedSize || false;
        this.maxWidth = options && options.maxWidth || Infinity;
        this.maxHeight = options && options.maxHeight || Infinity;
        this._resizeModal();
        this.getBody().scrollTop(0);
        if(cb) this.$modalDiv.on('shown', cb);
        this.$modalDiv.modal('show');
        return this;
    }

    hide(){
        this.$modalDiv.modal('hide');
        return this;
    }

    addHeader(html, options){
        var noClose = (options && options.noClose) || false,
            $el = this.$modalDiv.find('.modal-header');
        $el.html(html);
        if (!noClose) $el.prepend('<button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button>');
        return this;
    }

    addTitleLinkHeader(name, url, options){
        var txt = '<h4><a href="{0}" target="_blank">{1}</a></h4>'.printf(url, name);
        return this.addHeader(txt, options);
    }

    addFooter(html, options){
        var noClose = (options && options.noClose) || false,
            $el = this.$modalDiv.find('.modal-footer');
        $el.html(html);
        if (!noClose) $el.append('<button class="btn" data-dismiss="modal">Close</button>');
        return this;
    }

    getBody(){
        return this.$modalDiv.find('.modal-body');
    }

    addBody(html){
        this.getBody().html(html).scrollTop(0);
        return this;
    }

    _resizeModal(){
        var h = parseInt($(window).height(), 10),
            w = parseInt($(window).width(), 10),
            modalCSS = {
                width: '',
                height: '',
                top: '',
                left: '',
                margin: '',
                'max-height': '',
            },
            modalBodyCSS = {
                'max-height': '',
            };

        if(!this.fixedSize){
            var mWidth = Math.min(w-50, this.maxWidth),
                mWidthPadding = parseInt((w-mWidth)*0.5, 10),
                mHeight = Math.min(h-50, this.maxHeight);
            _.extend(modalCSS, {
                width: '{0}px'.printf(mWidth),
                top: '25px',
                left: '{0}px'.printf(mWidthPadding),
                margin: '0px',
                'max-height': '{0}px'.printf(mHeight),
            });
            _.extend(modalBodyCSS, {
                'max-height': '{0}px'.printf(mHeight-150),
            });
        }
        this.$modalDiv.css(modalCSS);
        this.getBody().css(modalBodyCSS);
    }

    getModal(){
        return this.$modalDiv;
    }
}

export default HAWCModal;
