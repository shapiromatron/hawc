import $ from '$';
import _ from 'underscore';
import d3 from 'd3';


class HAWCUtils {

    static booleanCheckbox(value){
        return (value) ? `<i class="fa fa-check"><span class="invisible">${value}</span></i>`:
            `<i class="fa fa-minus"><span class="invisible">${value}</span></i>`;
    }

    static newWindowPopupLink(triggeringLink) {
        // Force new window to be a popup window
        var href = triggeringLink.href + '?_popup=1';
        var win = window.open(href, '_blank', 'height=500,width=980,resizable=yes,scrollbars=yes');
        win.focus();
        return false;
    }

    static build_breadcrumbs(arr){
        // builds a string of breadcrumb hyperlinks for navigation
        var links = [];
        arr.forEach(function(v){
            links.push('<a target="_blank" href="{0}">{1}</a>'.printf(v.url, v.name));
        });
        return links.join('<span> / </span>');
    }

    static InitialForm(config){

        var selector_val = config.form.find('#id_selector_1'),
            submitter = config.form.find('#submit_form');

        submitter.on('click', function(){
            var val = parseInt(selector_val.val(), 10);
            if(val){
                submitter.attr('href', '{0}?initial={1}'.printf(config.base_url, val));
                return true;
            }
            return false;
        });
    }

    static prettifyVariableName(str){
        str = str.replace(/_/g, ' ');
        return str.charAt(0).toUpperCase() + str.substr(1);
    }

    static truncateChars(txt, n){
        n = n || 200;
        if (txt.length>n) return txt.slice(0, n) + '...';
        return txt;
    }

    static pageActionsButton(items){
        var $menu = $('<ul class="dropdown-menu">');
        items.forEach(function(d){
            if(d instanceof Object){
                $menu.append('<li><a href="{0}" class="{1}">{2}</a></li>'.printf(d.url, d.cls||'', d.text));
            } else if (typeof d === 'string'){
                $menu.append('<li class="disabled"><a tabindex="-1" href="#">{0}</a></li>'.printf(d));
            } else {
                console.error('unknown input type');
            }
        });
        return $('<div class="btn-group pull-right">')
            .append('<a class="btn btn-primary dropdown-toggle" data-toggle="dropdown">Actions <span class="caret"></span></a>')
            .append($menu);
    }

    static addAlert(content, $div){
        $div = $div || $('#content');
        $div.prepend($('<div class="alert">')
            .append('<button type="button" class="close" data-dismiss="alert">&times;</button>')
            .append(content));
    }

    static abstractMethod(){
        throw 'Abstract method; requires implementation';
    }

    static renderChemicalProperties(url, $div, show_header){
        $.get(url, function(data){
            if(data.status==='success'){

                var content = [],
                    ul = $('<ul>');

                ul.append('<li><b>Common name:</b> {0}</li>'.printf(data.CommonName))
                  .append('<li><b>SMILES:</b> {0}</li>'.printf(data.SMILES))
                  .append('<li><b>Molecular Weight:</b> {0}</li>'.printf(data.MW))
                  .append('<li><img src="data:image/jpeg;base64,{0}"></li>'.printf(data.image));

                if (show_header) content.push('<h3>Chemical Properties Information</h3>');

                content.push(ul,
                             '<p class="help-block">Chemical information provided by <a target="_blank" href="http://www.chemspider.com/">http://www.chemspider.com/</a></p>');
                $div.html(content);
            }
        });
    }

    static updateDragLocationTransform(setDragCB){
        // a new drag location, requires binding to d3.behavior.drag,
        // and requires a _.partial injection of th settings module.
        var getXY = function(txt){
            // expects an attribute like 'translate(277', '1.1920928955078125e-7)'
            if (_.isNull(txt) || txt.indexOf('translate') !== 0) return;
            var cmps = txt.split(',');
            return [
                parseFloat(cmps[0].split('(')[1], 10),
                parseFloat(cmps[1].split(')')[0], 10),
            ];
        };

        return d3.behavior.drag()
            .origin(Object)
            .on('drag', function(){
                var x, y,
                    p = d3.select(this),
                    coords = getXY(p.attr('transform'));

                if (coords){
                    x = parseInt(coords[0] + d3.event.dx, 10);
                    y = parseInt(coords[1] + d3.event.dy, 10);
                    p.attr('transform', `translate(${x},${y})`);
                    if(setDragCB){
                        setDragCB.bind(this)(x, y);
                    }
                }
            });
    }

    static updateDragLocationXY(setDragCB){
        // a new drag location, requires binding to d3.behavior.drag,
        // and requires a _.partial injection of th settings module.
        return d3.behavior.drag()
            .origin(Object)
            .on('drag', function(){
                var p = d3.select(this),
                    x = parseInt(parseInt(p.attr('x'), 10) + d3.event.dx, 10),
                    y = parseInt(parseInt(p.attr('y'), 10) + d3.event.dy, 10);

                p.attr('x', x);
                p.attr('y', y);
                if(setDragCB){
                    setDragCB.bind(this)(x, y);
                }
            });
    }

    static wrapText(text, max_width){
        if (!($.isNumeric(max_width)) || max_width<=0) return;
        var $text = d3.select(text),
            words = text.textContent.split(/\s+/).reverse(),
            word,
            line = [],
            lineNumber = 0,
            lineHeight = text.getBBox().height, // px
            x = $text.attr('x'),
            y = $text.attr('y'),
            tspan = $text.text(null)
                        .append('tspan')
                        .attr('x', x)
                        .attr('y', y);

        while(word = words.pop()){
            line.push(word);
            tspan.text(line.join(' '));
            if(tspan.node().getComputedTextLength() > max_width && line.length>1){
                line.pop();
                tspan.text(line.join(' '));
                line = [word];
                tspan = $text.append('tspan')
                             .attr('x', x)
                             .attr('y', y)
                             .attr('dy', ++lineNumber * lineHeight + 'px')
                             .text(word);
            }
        }
    }

    static isSupportedBrowser(){
        // not ideal; but <IE12 isn't supported which is primary-goal:
        // http://webaim.org/blog/user-agent-string-history/
        var ua = navigator.userAgent.toLowerCase(),
            isChrome = ua.indexOf('chrome') > -1,
            isFirefox = ua.indexOf('firefox') > -1,
            isSafari = ua.indexOf('safari') > -1;
        return isChrome || isFirefox || isSafari;
    }

    static browserCheck(){
        if (!HAWCUtils.isSupportedBrowser()){
            $('#content')
                .prepend($('<div class="alert">')
                .append('<button id="hideBrowserWarning" type="button" class="close" data-dismiss="alert">&times;</button>')
                .append('<b>Warning:</b> Your current browser has not been tested extensively with this website, which may result in some some errors with functionality. The following browsers are fully supported:<ul><li><a href="https://www.google.com/chrome/" target="_blank">Google Chrome</a> (preferred)</li><li><a href="https://www.mozilla.org/firefox/" target="_blank">Mozilla Firefox</a></li><li><a href="https://www.apple.com/safari/" target="_blank">Apple Safari</a></li></ul>Please use a different browser for an optimal experience.'));
        }
    }

    static buildUL(lst, func){
        return '<ul>{0}</ul>'.printf(_.map(lst, func).join(''));
    }

    static isHTML(str) {
        var a = document.createElement('div');
        a.innerHTML = str;
        for (var c = a.childNodes, i = c.length; i--; ) {
            if (c[i].nodeType == 1) return true;
        }
        return false;
    }
}

export default HAWCUtils;


