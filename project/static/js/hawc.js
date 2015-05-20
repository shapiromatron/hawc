SQColors = ["#E8E8E8", "#CC3333", "#FFCC00", "#6FFF00", "#00CC00"]; // todo: move into study object?

// Extend JS built-ins
Object.defineProperty(Object.prototype, "rename_property", {
  value: function(old_name, new_name){
    try{
        this[new_name] = this[old_name];
        delete this[old_name];
    } catch(f){}
  }
});
_.extend(Date.prototype, {
    toString: function(){
        var pad = function(x){return ((x<10) ? "0" : "") + x;};
        if(this.getTime()){
            d = pad(this.getDate());
            m = pad(this.getMonth()+1);
            y = this.getFullYear();
            hr = pad(this.getHours());
            min = pad(this.getMinutes());
            return [y, m, d].join('/') + ' ' + hr +  ':' + min;
        }
        return null;
    }
});
_.extend(String, {
    hex_to_rgb: function(hex){
        // http://stackoverflow.com/questions/5623838/
        hex = hex.replace(/^#?([a-f\d])([a-f\d])([a-f\d])$/i, function(m, r, g, b){
            return r + r + g + g + b + b;
        });

        var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
        return result ? {
            r: parseInt(result[1], 16),
            g: parseInt(result[2], 16),
            b: parseInt(result[3], 16)
        }:null;
    },
    contrasting_color: function(hex){
        // http://stackoverflow.com/questions/1855884/
        var rgb = String.hex_to_rgb(hex),
            a = 1 - (0.299 * rgb.r + 0.587 * rgb.g + 0.114 * rgb.b)/255;
        return (a<0.5)?'#000':'#fff';
    },
    random_string: function(){
        return 'xxxxxxxxxxxxxxx'.replace(/x/g, function(c){
            return String.fromCharCode(97+parseInt(26*Math.random()));
        });
    }
});
_.extend(String.prototype, {
    printf: function(){
        //http://stackoverflow.com/questions/610406/
        var args = arguments;
        return this.replace(/{(\d+)}/g, function(match, number){
            return typeof args[number] !== 'undefined' ? args[number] : match;
        });
    }
});
_.extend(Array.prototype, {
    splice_object: function(obj){
        if (this.length === 0) return this;
        for (var i = this.length-1; i>=0; i-=1){
            if(this[i] === obj){this.splice(i, 1);}
        }
    },
    getUnique: function(){
       var u = {}, a = [];
       for(var i = 0, l = this.length; i < l; ++i){
          if(u.hasOwnProperty(this[i])){continue;}
          a.push(this[i]);
          u[this[i]] = 1;
       }
       return a;
    }
});
_.extend(Math, {
    GammaCDF: function(x,a){
        // adapted from http://www.math.ucla.edu/~tom/distributions/gamma.html
        var Gcf = function(X,A){        // Good for X>A+1
            with (Math){
                var A0=0,
                    B0=1,
                    A1=1,
                    B1=X,
                    AOLD=0,
                    N=0;
                while (abs((A1-AOLD)/A1)>0.00001){
                    AOLD=A1;
                    N=N+1;
                    A0=A1+(N-A)*A0;
                    B0=B1+(N-A)*B0;
                    A1=X*A0+N*A1;
                    B1=X*B0+N*B1;
                    A0=A0/B1;
                    B0=B0/B1;
                    A1=A1/B1;
                    B1=1;
                }
                var Prob=exp(A*log(X)-X-GammaCDF.LogGamma(A))*A1;
            }
            return 1-Prob;
        },
        Gser = function(X,A){        // Good for X<A+1.
            with (Math){
                var T9=1/A,
                    G=T9,
                    I=1;
                while (T9>G*0.00001){
                    T9=T9*X/(A+I);
                    G=G+T9;
                    I=I+1;
                }
                G=G*exp(A*log(X)-X-GammaCDF.LogGamma(A));
            }
            return G;
        },
        LogGamma = function(Z){
            with (Math){
                var S = 1 + 76.18009173/Z-
                            86.50532033/(Z+1)+
                            24.01409822/(Z+2)-
                            1.231739516/(Z+3)+
                            0.00120858003/(Z+4)-
                            0.00000536382/(Z+5),
                    LG= (Z-0.5)*log(Z+4.5)-(Z+4.5)+log(S*2.50662827465);
            }
            return LG;
        },
        normalcdf = function(X){   //HASTINGS.  MAX ERROR = .000001
            var T=1/(1+0.2316419*Math.abs(X)),
                D=0.3989423*Math.exp(-X*X/2),
                Prob=D*T*(0.3193815+T*(-0.3565638+T*(1.781478+T*(-1.821256+T*1.330274))));
            if (X>0){
                Prob=1-Prob;
            }
            return Prob;
        },
        GI;

        if (x<=0){
            GI=0;
        } else if(a>200){
            var z=(x-a)/Math.sqrt(a);
            var y=Math.GammaCDF.normalcdf(z);
            var b1=2/Math.sqrt(a);
            var phiz=0.39894228*Math.exp(-z*z/2);
            var w=y-b1*(z*z-1)*phiz/6;  //Edgeworth1
            var b2=6/a;
            var u=3*b2*(z*z-3)+b1*b1*(z^4-10*z*z+15);
            GI=w-phiz*z*u/72;        //Edgeworth2
        }else if(x<a+1){
            GI=Math.GammaCDF.Gser(x,a);
        }else{
            GI=Math.GammaCDF.Gcf(x,a);
        }
        return GI;
    },
    Inv_tdist_05: function(df){
        // Calculates the inverse t-distribution using a piecewise linear form for
        // the degrees of freedom specified. Assumes a two-tailed distribution with
        // an alpha of 0.05. Based on curve-fitting using Excel's T.INV.2T function
        // with a maximum absolute error of 0.00924 and perent error of 0.33%.

        if (df < 1){
            return NaN;
        }else if(df == 1){
            return 12.7062047361747;
        }else if(df < 12){
            var b = [7.9703237683E-05,-3.5145890027E-03, 0.063259191874,
                    -0.59637230750, 3.1294134410, -8.8538894383, 13.358101926];
        }else if(df < 62){
            var b = [1.1184055716E-10, -2.7885328039E-08, 2.8618499662E-06,
                     -1.5585120701E-04, 4.8300645273E-03, -0.084316656676,
                     2.7109288893];
        }else{
            var b = [5.1474329765E-16, -7.2622263880E-13, 4.2142967681E-10,
                     -1.2973354626E-07, 2.2753080520E-05, -2.2594979441E-03,
                     2.0766977669E+00];
            if (df > 350){
                console.log("Warning, extrapolating beyond range for which regression was designed.");
            }
        }
        return b[0]*Math.pow(df,6) + b[1]*Math.pow(df,5) + b[2]*Math.pow(df,4) +
               b[3]*Math.pow(df,3) + b[4]*Math.pow(df,2) + b[5]*Math.pow(df,1) +
               b[6];
    },
    og10: function(val){
      return Math.log(val) / Math.LN10;
    },
    ltqnorm: function(p){
       /*
        * Modified from the author's original python code (original comments t
        * follow below) by shapiromatron@gmail.com.  February 18, 2013.
        *
        * Lower tail quantile for standard normal distribution function.
        *
        * This function returns an approximation of the inverse cumulative
        * standard normal distribution function.  I.e., given P, it returns
        * an approximation to the X satisfying P = Pr{Z <= X} where Z is a
        * random variable from the standard normal distribution.
        *
        * The algorithm uses a minimax approximation by rational functions
        * and the result has a relative error whose absolute value is less
        * than 1.15e-9.
        *
        * Author:      Peter John Acklam
        * Time-stamp:  2000-07-19 18:26:14
        * E-mail:      pjacklam@online.no
        * WWW URL:     http://home.online.no/~pjacklam
        */

        if ((p <= 0) || (p >= 1)){
            // Alert console of error
            console.log("Argument to ltqnorm  must be in open interval (0,1)");
        }

        // Coefficients in rational approximations.
        a = [-3.969683028665376e+01,  2.209460984245205e+02, -2.759285104469687e+02,
              1.383577518672690e+02, -3.066479806614716e+01,  2.506628277459239e+00];
        b = [-5.447609879822406e+01,  1.615858368580409e+02, -1.556989798598866e+02,
              6.680131188771972e+01, -1.328068155288572e+01];
        c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
             -2.549732539343734e+00,  4.374664141464968e+00,  2.938163982698783e+00];
        d = [7.784695709041462e-03,  3.224671290700398e-01, 2.445134137142996e+00,
             3.754408661907416e+00];

        // Define break-points.
        plow  = 0.02425;
        phigh = 1 - plow;

        // Rational approximation for lower region:
        if (p < plow){
           q  = Math.sqrt(-2*Math.log(p));
           return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) /
                  ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1);
        }

        // Rational approximation for upper region:
        if (phigh < p){
           q  = Math.sqrt(-2*Math.log(1-p));
           return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) /
                   ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1);
        }

        // Rational approximation for central region:
        q = p - 0.5;
        r = q*q;
        return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q /
               (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1);
    },
    normalcdf: function(mean, sigma, to){
        // http://stackoverflow.com/questions/5259421/
        var z = (to-mean)/Math.sqrt(2*sigma*sigma);
        var t = 1/(1+0.3275911*Math.abs(z));
        var a1 =  0.254829592;
        var a2 = -0.284496736;
        var a3 =  1.421413741;
        var a4 = -1.453152027;
        var a5 =  1.061405429;
        var erf = 1-(((((a5*t + a4)*t) + a3)*t + a2)*t + a1)*t*Math.exp(-z*z);
        var sign = 1;
        if(z<0){sign = -1;}
        return (1/2)*(1+sign*erf);
    },
    mean: function(array){
        switch(array.length){
            case 0:
                return null;
            case 1:
                return array[0];
            default:
                var sum=0, err=false;
                array.forEach(function(v){if(typeof(v)!=='number'){err = true;} sum += v;});
        }
        if((err===false) && (isFinite(sum))){
            return sum/array.length;
        }else{
            return null;
        }
    },
    stdev: function(array){
        // calculates sample standard-deviation (n-1)
        var sum = 0,  mean = Math.mean(array);
        if(mean === null) return null;
        array.forEach(function(v){
            sum += (v-mean)*(v-mean);
        });
        return Math.sqrt(sum/(array.length-1));
    }
});


// Django AJAX with CSRF protection.
var getCookie = function(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
},
csrftoken = getCookie('csrftoken'),
sessionid = getCookie('sessionid'),
csrfSafeMethod = function(method) {
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));  // safe methods
};
$.ajaxSetup({
    crossDomain: false,
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type)) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
            xhr.setRequestHeader("sessionid", sessionid);
        }
    }
});


// Utility functions in custom namespace
var HAWCUtils = {
    booleanCheckbox: function(value){
        return (value) ? "☑" : "☒";
    },
    newWindowPopupLink: function(triggeringLink) {
        //Force new window to be a popup window
        href = triggeringLink.href + '?_popup=1';
        var win = window.open(href, "_blank", 'height=500,width=800,resizable=yes,scrollbars=yes');
        win.focus();
        return false;
    },
    dfUpdateElementIndex: function(el, prefix, ndx) {
        // Dynamic formset, modified from https://djangosnippets.org/snippets/1389/
        var id_regex = new RegExp('(' + prefix + '-\\d+)'),
            replacement = prefix + '-' + ndx;
        if ($(el).attr("for")) $(el).attr("for", $(el).attr("for").replace(id_regex, replacement));
        if (el.id) el.id = el.id.replace(id_regex, replacement);
        if (el.name) el.name = el.name.replace(id_regex, replacement);
    },
    dfAddForm: function(btn, prefix) {
        // Dynamic formset, modified from https://djangosnippets.org/snippets/1389/
        var formCount = parseInt($('#id_' + prefix + '-TOTAL_FORMS').val(), 10),
            row = $('.dynamic-form:last').clone(false).get(0);
        $(row).removeAttr('id').insertAfter($('.dynamic-form:last')).children('.hidden').removeClass('hidden');
        $(row).children().not(':last').children().each(function() {
            HAWCUtils.dfUpdateElementIndex(this, prefix, formCount);
            $(this).val('');
        });
        $(row).find('.delete-row').click(function() {
            HAWCUtils.dfDeleteForm(this, prefix);
        });
        $('#id_' + prefix + '-TOTAL_FORMS').val(formCount + 1);
        $(row).trigger('dynamicFormset-formAdded');
        return false;
    },
    dfDeleteForm: function(btn, prefix) {
        // Dynamic formset, modified from https://djangosnippets.org/snippets/1389/
        $(btn).parents('.dynamic-form').remove();
        var forms = $('.dynamic-form');
        $('#id_' + prefix + '-TOTAL_FORMS').val(forms.length);
        for (var i=0, formCount=forms.length; i<formCount; i++) {
            $(forms.get(i)).children().not(':last').children().each(function() {
                HAWCUtils.dfUpdateElementIndex(this, prefix, i);
            });
        }
        $(forms).trigger('dynamicFormset-formRemoved');
        return false;
    },
    build_breadcrumbs: function(arr){
        // builds a string of breadcrumb hyperlinks for navigation
        var links = [];
        arr.forEach(function(v){
            links.push('<a target="_blank" href="{0}">{1}</a>'.printf(v.url, v.name));
        });
        return links.join('<span> / </span>');
    },
    InitialForm: function(config){

        var selector = config.form.find('#id_selector_0'),
            selector_val = config.form.find('#id_selector_1'),
            submitter = config.form.find('#submit_form');

        selector.djselectable('option', 'prepareQuery', function(qry){
            qry.related = config.related;
        });

        submitter.on('click', function(){
            var val = parseInt(selector_val.val(), 10);
            if(val){
                submitter.attr('href', "{0}?initial={1}".printf(config.base_url, val));
                return true;
            }
            return false;
        });
    },
    prettifyVariableName: function(str){
        str = str.replace(/_/g, ' ');
        return str.charAt(0).toUpperCase() + str.substr(1);
    },
    truncateChars: function(txt, n){
        n = n || 200;
        if (txt.length>n) return txt.slice(0, n) + "...";
        return txt;
    },
    pageActionsButton: function(items){
        var $menu = $('<ul class="dropdown-menu">');
        items.forEach(function(d){
            $menu.append('<li><a href="{0}">{1}</a></li>'.printf(d.url, d.text));
        });
        return $('<div class="btn-group pull-right">')
            .append("<a class='btn btn-primary dropdown-toggle' data-toggle='dropdown'>Actions <span class='caret'></span></a>")
            .append($menu)
    },
    addAlert: function(content, $div){
        $div = $div || $("#content");
        $div.prepend($('<div class="alert">')
            .append('<button type="button" class="close" data-dismiss="alert">&times;</button>')
            .append(content));
    },
    abstractMethod: function(){
        throw "Abstract method; requires implementation";
    },
    renderChemicalProperties: function(url, $div, show_header){
        $.get(url, function(data){
            if(data.status==="success"){

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
};

// Observer design pattern; observers require an `update` method.
var Observee = function(){
    this._observers = [];
};
Observee.prototype = {
    addObserver: function(obj){
        this._observers.push(obj);
    },
    removeObserver: function(obj){
        var idx = this._observers.indexOf(obj);
        if (idx>=0) this._observers.splice(idx, 1);
    },
    notifyObservers: function(msg){
        this._observers.forEach(function(d){
            d.update(msg);
        });
    }
};


// Version object. Used to generate diffs to compare a list of objects.
var Version = function(object_list, list_table_id, comparison_table_id){
    /*
     * Requires an object_list, which is an array of a specified object-type.
     * This object-type MUST contain a static variable named field_order so that
     * the table can properly be rendered with fields in the correct order. The
     * object-type MUST also generate a banner field which will be used for the
     * table-headers.
     *
     * Also requires CSS-style lookups for the list of revisions table and the
     * comparison table. The list of revisions table is assumed to have one
     * column for listing the possible revisions. The comparison table is assumed
     * to have two columns- the first-column  (left unchanged) is the description
     * of fields to be presented in the same order as field_order, and the second-
     * column is the column which will be written to.
     */
    this.object_list = object_list;
    this.tbl_list = $(list_table_id);
    this.tbl_compare = $(comparison_table_id);

    this.build_list_table();

    var e = jQuery.Event("click");
    $($(this.tbl_list).find('tbody tr')[0]).trigger(e);
};
Version.prototype =  {
    build_list_table: function(){
        // Build table that shows list of available revision versions
        var v = this;
        tbody = $('<tbody></tbody>');
        $(this.object_list).each(function(i, v){
            var tr = $('<tr><td>' + v.banner + '</td></tr>').data('d', v);
            tbody.append(tr);
        });
        $(this.tbl_list.find('tbody')).html(tbody);

        $(this.tbl_list).on('click','tbody tr', function(e){
            var d = $(this).data('d');
            if (e.ctrlKey || e.metaKey){
                v.secondary = d;
                $(this).parent().find('tr').removeClass('version_secondary');
                $(this).addClass('version_secondary');
            }else{
                v.primary = d;
                $(this).parent().find('tr').removeClass('version_primary');
                $(this).addClass('version_primary');
                v.secondary = undefined;
                $(this).parent().find('tr').removeClass('version_secondary');
            }
            v.load_comparison_table();
        });
    },
    load_comparison_table: function(){
        // build the actual comparison table
        var fields = this.primary.constructor.field_order,
            l = fields.length,
            trs = this.tbl_compare.find('tbody tr'), val;

        // add header
        if(!this.secondary){
            $(this.tbl_compare.find('tfoot')).addClass('hidden');
            $(this.tbl_list.find('tfoot')).addClass('hidden');
            $(this.tbl_compare.find('thead th')[1]).html(this.primary.banner);
        }else{
            $(this.tbl_compare.find('tfoot')).removeClass('hidden');
            $(this.tbl_list.find('tfoot')).removeClass('hidden');
            $(this.tbl_compare.find('thead th')[1]).html('Comparing ' + this.primary.banner +
                                                         '<br>to ' + this.secondary.banner);
        }

        // add fields
        for(var i=0; i<l; i++){
            val = this.return_diff_html(fields[i]);
            $(trs[i]).children().eq(1).html(val);
        }
    },
    return_diff_html: function(field){
        if (!this.secondary){
            // console.log(typeof(this.primary[field]));
            return String(this.primary[field]);
        }else{
            var dmp = new diff_match_patch(),
                d = dmp.diff_main(String(this.secondary[field]),
                                  String(this.primary[field]));
            dmp.diff_cleanupSemantic(d);
            var txt = dmp.diff_prettyHtml_hawc(d);
            return this._cleanup_hack(txt);
        }
    },
    _cleanup_hack: function(txt){
        txt = txt.replace(/\&lt;/g,'<');
        txt = txt.replace(/\&gt;/g,'>');
        txt = txt.replace(/\&nbsp;/g,' ');
        return txt;
    }
};
if(diff_match_patch){
    // Monkey-patch HAWC-object version diffs
    _.extend(diff_match_patch.prototype, {
        diff_prettyHtml_hawc: function(diffs) {
            // Revised to use HAWC html classes.
            var html = [];
            var pattern_amp = /&/g;
            var pattern_lt = /</g;
            var pattern_gt = />/g;
            var pattern_para = /\n/g;
            for (var x = 0; x < diffs.length; x++) {
                var op = diffs[x][0];    // Operation (insert, delete, equal)
                var data = diffs[x][1];  // Text of change.
                var text = data.replace(pattern_amp, '&amp;').replace(pattern_lt, '&lt;')
                               .replace(pattern_gt, '&gt;').replace(pattern_para, '<br>');
                switch (op) {
                    case DIFF_INSERT:
                    html[x] = '<span class="diff-insert">' + text + '</span>';
                    break;
                case DIFF_DELETE:
                    html[x] = '<span class="diff-delete">' + text + '</span>';
                    break;
                case DIFF_EQUAL:
                    html[x] = '<span>' + text + '</span>';
                    break;
                }
            }
            return html.join('');
        }
    });
}


// Generic parent for all d3.js visualizations
var D3Plot = function(){
    // add one div to be used for tooltips
    if(!this.tooltip){
        this.tooltip = d3.select("body").append("div")
                                .attr("class", "d3hovertooltip")
                                .style("opacity", 0);
    }
};
D3Plot.prototype = {
    add_title: function(x, y){
        x = x || (this.w/2);
        y = y || (-this.padding.top/2);

        if (this.title){this.title.remove();}
        this.title = this.vis.append("svg:text")
        .attr("x", x)
        .attr("y", y)
        .attr("text-anchor", "middle")
        .attr("class","dr_title")
        .html(this.title_str);
    },
    add_final_rectangle: function(){
        // Add final rectangle around plot.
        if(this.bounding_rectangle) this.bounding_rectangle.remove();
        this.bounding_rectangle = this.vis.append("rect")
                                      .attr("width", this.w)
                                      .attr("height", this.h)
                                      .attr("class", 'bounding_rectangle');
    },
    set_legend_location: function(top, left){
        this.legend_top = top;
        this.legend_left = left;
    },
    build_legend: function(settings){
        var plot = this,
            buffer = settings.box_padding, //shortcut reference
            drag = d3.behavior.drag()
                .origin(Object)
                .on("drag", function(d,i){
                    var regexp = /\((-?[0-9]+)[, ](-?[0-9]+)\)/,
                        p = d3.select(this),
                        m = regexp.exec(p.attr("transform"));
                        if (m !== null && m.length===3){
                            var x = parseFloat(m[1]) + d3.event.dx,
                                y = parseFloat(m[2]) + d3.event.dy;
                            p.attr("transform", "translate(" + x + "," + y + ")");
                            plot.set_legend_location(y, x);
                        }
                    });

        this.legend = this.vis.append("g")
                        .attr('class', 'plot_legend')
                        .attr("transform", "translate(" + settings.box_l + "," + settings.box_t + ")")
                        .attr("cursor", "pointer")
                        .attr("data-buffer", buffer)
                        .call(drag);

        this.set_legend_location(settings.box_t, settings.box_l);

        this.legend.append("svg:rect")
                .attr("class","legend")
                .attr("height", 10)
                .attr("width", 10);

        this.legend.selectAll("legend_circles")
            .data(settings.items)
            .enter()
            .append("circle")
                .attr("cx", settings.dot_r + buffer)
                .attr("cy", function(d, i){return buffer*2 + i*settings.item_height;} )
                .attr("r", settings.dot_r)
                .attr('class', function(d, i){return "legend_circle " + d.classes;})
                .attr('fill', function(d, i){return d.color;});

        this.legend.selectAll("legend_text")
            .data(settings.items)
            .enter()
            .append("svg:text")
                .attr("x", 2*settings.dot_r + buffer*2)
                .attr("class", "legend_text")
                .attr("y", function(d, i){return buffer*2 + settings.dot_r + i*settings.item_height;})
                .text(function(d, i){ return d.text;});

        this.resize_legend();
    },
    resize_legend: function(){
        // resize legend box that encompasses legend items
        // NOTE that this requires the image to be rendered into DOM
        if(this.legend){
            var buffer = parseInt(this.legend.attr('data-buffer')),
                dim = this.legend.node().getBoundingClientRect();
            this.legend.select('.legend').attr('width', dim.width+buffer)
                                         .attr('height', dim.height+buffer);
        }
    },
    build_plot_skeleton: function(background){
        //Basic plot setup to set size and positions
        var self=this,
            w = this.w + this.padding.left + this.padding.right,
            h = this.h + this.padding.top + this.padding.bottom;

        //clear plot div and and append new svg object
        this.plot_div.empty();
        this.vis = d3.select(this.plot_div[0])
          .append("svg")
            .attr("width", w)
            .attr("height", h)
            .attr("class", "d3")
            .attr("viewBox", "0 0 {0} {1}".printf(w, h))
            .attr("preserveAspectRatio", "xMinYMin")
          .append("g")
            .attr("transform", "translate({0},{1})".printf(this.padding.left, this.padding.top));
        this.svg = this.vis[0][0].parentNode;

        var chart = $(this.svg),
            container = chart.parent();

        this.full_width = w;
        this.full_height = h;
        this.isFullSize = true;
        this.trigger_resize = function(forceResize){
            var targetWidth = Math.min(container.width(), self.full_width),
                currentWidth = chart.width(),
                aspect = self.full_width / self.full_height;
            if(forceResize===true && !self.isFullSize) targetWidth = self.full_width;

            if (targetWidth !== self.full_width){
                // use custom smaller size
                chart.attr("width", targetWidth);
                chart.attr("height", Math.round(targetWidth / aspect));
                self.isFullSize = false;
                if(self.resize_button){
                    self.resize_button.attr("title", "zoom figure to full-size");
                    self.resize_button.find('i').attr('class', 'icon-zoom-in');
                }
            } else {
                // set back to full-size
                chart.attr("width", self.full_width);
                chart.attr("height", self.full_height);
                self.isFullSize = true;
                if(self.resize_button){
                    self.resize_button.attr("title", "zoom figure to fit screen");
                    self.resize_button.find('i').attr('class', 'icon-zoom-out');
                }
            }
        };
        $(window).resize(this.trigger_resize);

        // add gray background to plot.
        if(background){
            this.vis.append("rect")
                .attr("x", 0)
                .attr("y", 0)
                .attr("height", this.h)
                .attr("width", this.w)
                .attr("class", "dp_bg");
        }
    },
    build_x_label: function(x, y){

        x = x || (this.w/2);
        y = y || (this.h + this.padding.bottom - 5);

        if (this.x_axis_label){this.x_axis_label.remove();}
        this.x_axis_label = this.vis.append("svg:text")
            .attr("x", x)
            .attr("y", y)
            .attr("text-anchor", "middle")
            .attr("class","dr_axis_labels x_axis_label")
            .text(this.x_label_text);
    },
    build_y_label: function(x, y){

        x = x || (-this.h/2);
        y = y || (-this.padding.left + 15);

        if (this.y_axis_label){this.y_axis_label.remove();}
        this.y_axis_label = this.vis.append("svg:text")
            .attr("x", x)
            .attr("y", y)
            .attr("transform",'rotate(270)')
            .attr("text-anchor", "middle")
            .attr("class","dr_axis_labels y_axis_label")
            .text(this.y_label_text);
    },
    _build_scale: function(settings){
        var scale;
        switch(settings.scale_type){
            case 'log':
              scale = d3.scale.log()
                    .clamp(true)
                    .domain(settings.domain)
                    .rangeRound(settings.rangeRound)
                    .nice();
              break;
            case 'linear':
              scale = d3.scale.linear()
                .clamp(true)
                .domain(settings.domain)
                .rangeRound(settings.rangeRound)
                .nice();
              break;
            case 'ordinal':
              scale = d3.scale.ordinal()
                .domain(settings.domain)
                .rangeRoundBands(settings.rangeRound);
              break;
            default:
              console.log('Error- settings.scale_type is not defined: ' + settings.scale_type);
            }
        return scale;
    },
    _print_axis: function(scale, settings){
        var axis = d3.svg.axis()
                .scale(scale)
                .orient(settings.text_orient);

        switch(settings.scale_type){
            case 'log':
                axis.ticks(1, settings.label_format);
                break;
            case 'linear':
                axis.ticks(settings.number_ticks);
                if (settings.label_format !== undefined){
                    axis.tickFormat(settings.label_format);
                }
                break;
        }

        if (settings.axis_labels){
            this.vis.append("g")
                .attr("transform", "translate(" + (settings.x_translate) + "," +
                      (settings.y_translate) + ")")
                .attr("class", settings.axis_class)
                .call(axis);
        }
        return axis;
    },
    _print_gridlines: function(scale, settings, line_settings){
        if (!settings.gridlines){return undefined;}

        var gridline_data;
        switch(settings.scale_type){
            case 'log':
            case 'linear':
                gridline_data = scale.ticks(settings.number_ticks);
                break;
            case 'ordinal':
                gridline_data = scale.domain();
                break;
        }

        var gridlines = this.vis.append("g")
                        .attr('class', settings.gridline_class);

        gridlines.selectAll("gridlines")
            .data(gridline_data).enter()
            .append("svg:line")
            .attr("x1", line_settings[0])
            .attr("x2", line_settings[1])
            .attr("y1", line_settings[2])
            .attr("y2", line_settings[3])
            .attr("class", settings.gridline_class);

        return gridlines;
    },
    rebuild_y_axis: function(){
        //rebuild y-axis
        this.yAxis
            .scale(this.y_scale)
            .ticks(this.y_axis_settings.number_ticks,
                   this.y_axis_settings.label_format);

        this.vis.selectAll('.y_axis')
            .transition()
            .duration(1000)
            .call(this.yAxis);
    },
    rebuild_y_gridlines: function(options){
        // rebuild y-gridlines

        var duration = (options.animate) ? 1000 : 0;

        this.y_primary_gridlines = this.vis.select("g.y_gridlines").selectAll('line')
            .data(this.y_scale.ticks(this.y_axis_settings.number_ticks));

        this.y_primary_gridlines
            .enter().append("line")
               .attr("class", this.y_axis_settings.gridline_class)
               .attr("y1", function(v){return v;})
               .attr("y2", function(v){return v;})
               .attr("x1", 0)
               .attr("x2", 0);

        this.y_primary_gridlines
            .transition()
            .duration(duration)
            .attr("y1", this.y_scale)
            .attr("y2", this.y_scale)
            .attr("x2", this.w);

        this.y_primary_gridlines.exit()
            .transition()
            .duration(duration/2)
            .attr("x2", 0)
            .remove();
    },
    rebuild_x_axis: function(){
        //rebuild x-axis
        this.xAxis
            .scale(this.x_scale)
            .ticks(this.x_axis_settings.number_ticks,
                   this.x_axis_settings.label_format);

        this.vis.selectAll('.x_axis')
            .transition()
            .duration(1000)
            .call(this.xAxis);
    },
    rebuild_x_gridlines: function(options){
        // rebuild x-gridlines

        var duration = (options.animate) ? 1000 : 0;

        this.x_primary_gridlines = this.vis.select("g.x_gridlines").selectAll('line')
            .data(this.x_scale.ticks(this.x_axis_settings.number_ticks));

        this.x_primary_gridlines
            .enter().append("line")
               .attr("class", this.x_axis_settings.gridline_class)
               .attr("x1", function(v){return v;})
               .attr("x2", function(v){return v;})
               .attr("y1", 0)
               .attr("y2", 0);

        this.x_primary_gridlines
            .transition()
            .duration(duration)
            .attr("x1", this.x_scale)
            .attr("x2", this.x_scale)
            .attr("y2", this.h);;

        this.x_primary_gridlines.exit()
            .transition()
            .duration(duration/2)
            .attr("y2", 0)
            .remove();
    },
    build_y_axis: function(){
        // build y-axis based on plot-settings
        this.y_scale = this._build_scale(this.y_axis_settings);
        this.yAxis = this._print_axis(this.y_scale, this.y_axis_settings);
        this.y_primary_gridlines = this._print_gridlines(
                this.y_scale, this.y_axis_settings,
                [0, this.w, this.y_scale, this.y_scale]);
    },
    build_x_axis: function(){
        // build x-axis based on plot-settings
        this.x_scale = this._build_scale(this.x_axis_settings);
        this.xAxis = this._print_axis(this.x_scale, this.x_axis_settings);
        this.x_primary_gridlines = this._print_gridlines(
                this.x_scale, this.x_axis_settings,
                [this.x_scale, this.x_scale, 0, this.h]);
    },
    build_line: function(options, existing){
        // build or update an existing line
        var l = existing;
        if(existing){
            existing
                .data(options.data || l.data())
                .transition()
                .delay(options.delay || 0)
                .duration(options.duration || 1000)
                    .attr("x1", options.x1 || function(v,i){ return d3.select(this).attr("x1");})
                    .attr("x2", options.x2 || function(v,i){ return d3.select(this).attr("x2");})
                    .attr("y1", options.y1 || function(v,i){ return d3.select(this).attr("y1");})
                    .attr("y2", options.y2 || function(v,i){ return d3.select(this).attr("y2");});
        }else{
            var append_to = options.append_to || this.vis;
            l = append_to.selectAll("svg.bars")
                .data(options.data)
                .enter()
                .append("line")
                    .attr("x1", options.x1)
                    .attr("y1",  options.y1)
                    .attr("x2", options.x2)
                    .attr("y2", options.y2)
                    .attr('class', options.classes);
        }
        return l;
    },
    isWithinDomain: function(event){
        // check that event is within plot domain
        var v = d3.mouse(event);
        return !((v[1]>this.h) || (v[1]<0) || (v[0]<0) || (v[0]>this.w));
    },
    add_menu: function(){
        if(this.menu_div) return;  // singleton
        var plot = this;

        // show cog to toggle options menu
        this.cog = this.vis.append('foreignObject')
            .attr('x', this.w + this.padding.right - 20)
            .attr('y', -this.padding.top + 5)
            .attr('width', 30)
            .attr('height', 30);

        this.cog_button = this.cog.append('xhtml:a')
            .attr('title', 'Display plot menu')
            .attr('class', 'hidden')
            .on('click', function(v,i){plot._toggle_menu_bar();});
        this.cog_button.append('xhtml:i')
                .attr('class', "icon-cog");

        // add menu below div
        this.menu_div = $('<div class="options_menu"></div>');
        this.plot_div.append(this.menu_div);

        // add close button to menu
        var close_button = {id:'close',
                            cls: 'btn btn-mini pull-right',
                            title: 'Hide menu',
                            text: 'x',
                            on_click: function(){plot._toggle_menu_bar();}};
        this.add_menu_button(close_button);

        this._add_download_buttons();

        // add zoom button to menu
        var zoom_button = {id:'close',
                           cls: 'btn btn-mini pull-right',
                           title: 'Zoom image to full-size',
                           text: '',
                           icon: 'icon-zoom-in',
                           on_click: function(){plot.trigger_resize(true);}};
        this.resize_button = this.add_menu_button(zoom_button);
    },
    _add_download_buttons: function(){
        var plot = this,
            group = $('<div class="pull-right btn-group"></div>'),
            dropdown = $('<a title="Download figure" class="btn btn-mini dropdown-toggle" data-toggle="dropdown" href="#"><i class="icon-download-alt"></i></a>'),
            dropdown_li = $('<ul class="dropdown-menu"></ul>'),
            svg = $('<li></li>').append(('<a href="#">Download as a SVG</a>'))
                    .on('click', function(e){e.preventDefault(); plot._download_image({"format": "svg"});}),
            pptx = $('<li></li>').append(('<a href="#">Download as a PPTX</a>'))
                    .on('click', function(e){e.preventDefault(); plot._download_image({"format": "pptx"});}),
            png = $('<li></li>').append(('<a href="#">Download as a PNG</a>'))
                    .on('click', function(e){e.preventDefault(); plot._download_image({"format": "png"});}),
            pdf = $('<li></li>').append(('<a href="#">Download as a PDF</a>'))
                    .on('click', function(e){e.preventDefault(); plot._download_image({"format": "pdf"});});
        dropdown_li.append(svg, pptx, png, pdf);
        group.append(dropdown, dropdown_li);
        this.menu_div.append(group);
    },
    add_menu_button: function(options){
        // add a button to the options menu
        var a = $('<a></a>')
            .attr("id", options.id)
            .attr('class', options.cls)
            .attr('title',options.title)
            .text(options.text || '')
            .on('click', options.on_click);
        if (options.icon){
            var icon = $('<i></i>').addClass(options.icon);
            a.append(icon);
        }
        this.menu_div.append(a);
        return a;
    },
    _toggle_menu_bar: function(){
        $(this.menu_div).toggleClass('hidden');
        $(this.cog_button).toggleClass('hidden');
    },
    _download_image: function(options){
        var svg_blob = this._save_to_svg(),
            form = $('<form style="display: none;" action="/assessment/download-plot/" method="post"></form>')
                .html(['<input name="height" value="{0}">'.printf(svg_blob.height),
                       '<input name="width" value="{0}">'.printf(svg_blob.width),
                       '<input name="svg" value="{0}">'.printf(btoa(escape(svg_blob.source[0]))),
                       '<input name="output" value="{0}">'.printf(options.format)]);
        form.appendTo('body').submit();
    },
    _save_to_svg: function(){
        // save svg and css styles to this document as a blob.
        // Adapted from SVG-Crowbar: http://nytimes.github.com/svg-crowbar/
        // Removed CSS style-grabbing components as this behavior was unreliable.

        function get_selected_svg(svg){
            svg.attr("version", "1.1");
            if (svg.attr("xmlns") === null){svg.attr("xmlns", d3.ns.prefix.svg);}
            var source = (new XMLSerializer()).serializeToString(svg.node()),
                rect = svg.node().getBoundingClientRect();
            return {
                "top": rect.top,
                "left": rect.left,
                "width": rect.width,
                "height": rect.height,
                "classes": svg.attr("class"),
                "id": svg.attr("id"),
                "childElementCount": svg.node().childElementCount,
                "source": [doctype + source]};
        }

        var doctype = '<?xml version="1.0" standalone="no"?><!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">',
            svg = d3.select(this.svg),
            svg_object = get_selected_svg(svg);

        svg_object.blob = new Blob(svg_object.source, {"type" : "text\/xml"});
        return svg_object;
    },
    show_tooltip: function(title, content){
        // used for hovering-only
        this.tooltip.transition()
                    .delay(800)
                    .duration(200)
                    .style("opacity", 1.0);

        this.tooltip.html('<h3 class="popover-title">' + title + '</h3><div class="popover-content">' + content + '</div>')
            .style("left", (d3.event.pageX + 10) + "px")
            .style("top", (d3.event.pageY - 20) + "px");
    },
    hide_tooltip: function(){
        this.tooltip.transition()
                    .duration(500)
                    .style("opacity", 0);
    }
};


// Generic tooltip
var PlotTooltip = function(styles){
    var self = this;
    this.tooltip_title = $('<h3 class="popover-title" title="drag to reposition"></h3>');
    this.tooltip_body = $('<div class="popover-content"></div>');

    this.tooltip = $('<div class="d3plottooltip" style="display: none;"></div>')
        .css(styles || {})
        .append(this.tooltip_title)
        .append(this.tooltip_body)
        .draggable()
        .resizable({"handles": "se", "autoHide": true})
        .appendTo('body');
    this.close_button = $('<button type="button" title="click or press ESC to close" class="close">&times;</button>');

    $(document).keyup(function(e){if(e.keyCode === 27){self.hide_tooltip();}});
    $('.d3plottooltip').on('click', '.close', function(){self.hide_tooltip();});
};
PlotTooltip.prototype = {
    display_endpoint: function(endpoint, e){
        var title  = '<small><b>{0}</b></small>'.printf(endpoint.build_breadcrumbs()),
            plot_div = $('<div style="height:300px; width:300px"></div'),
            details_div = $("<div></div>"),
            content = [details_div,
                       plot_div,
                       endpoint.build_endpoint_table($('<table class="table table-condensed table-striped"></table>'))];
        endpoint.build_details_table(details_div);
        this._show_tooltip(title, content, e);
        new EndpointPlotContainer(endpoint, plot_div);
    },
    display_comments: function(comment_manager, e){
        var title='Comments for {0}'.printf(comment_manager.object.data.title),
            content=[];
        comment_manager.$div = $('<div></div>');
        if(comment_manager.data.commenting_public){
            comment_manager._build_comment_list(content);
        }
        if(comment_manager.data.commenting_enabled){
            var form = $('<form"></form>');
            comment_manager._create_comment_form(form);
            content.push(form);
        }
        comment_manager.$div.html(content);
        this._show_tooltip(title, comment_manager.$div, e);
    },
    display_exposure_group_table: function(heg, e){
        var title = $('<span class="lead">').text("Exposure Group Details: " + heg.data.exposure_group.description),
            div = $('<div>');

        heg.build_exposure_group_table(div);
        this._show_tooltip(title, div, e);
    },
    _calculate_position: function(){
        // Determine the top and left coordinates for the popup box. Tries to put
        // to the right, then the left, then above, then below, and then finally if
        // none work, stick in the top-right corner.
        var top_padding=55, // larger padding due to HAWC toolbar
            padding = 10,
            off_x = window.pageXOffset,
            off_y = window.pageYOffset,
            width = this.tooltip.width(),
            half_width = width/2,
            height = this.tooltip.height(),
            half_height = height/2,
            x = this.event.pageX - off_x,
            y = this.event.pageY - off_y,
            wh = window.innerHeight,
            ww = $('body').innerWidth(),  // includes scrollbar
            l, t;

        if((x-width-padding>0)||(x+width+padding<ww)){
            // see if whole thing fits to left or right
            l = (x+width+padding<ww) ? (x+padding) : x-width-padding;
            t = (y-half_height-top_padding>0) ? y-half_height : top_padding;
            t = (t+height+padding>wh) ? wh-height-padding : t;
        } else if((y-height-top_padding>0)||(y+height+padding<wh)){
            // see if whole thing will fit above or below
            t = (y-height-top_padding>0) ? y-height-padding : y+padding;
            l = (x-half_width>0) ? x-half_width : 0;
            l = (l+width+padding>ww) ? ww-width-padding : l;
        } else {
            // put at top-right of window
            t = top_padding;
            l = ww-width-padding;
        }

        return {"top": (t + off_y) + "px", "left": (l + off_x) + "px"};
    },
    _show_tooltip: function(title, content, e, plot_object){
        this.tooltip_title.html([this.close_button, title]);
        this.tooltip_body.html(content);
        this.show_tooltip(e);
    },
    hide_tooltip: function(){this.tooltip.fadeOut("slow");},
    show_tooltip: function(e){
        this.event = e;
        this.tooltip.css(this._calculate_position()).fadeIn("slow").scrollTop();
    }
};


// Generic modal
var HAWCModal = function(){
    // singleton modal instance
    var $modalDiv = $('#hawcModal');
    if ($modalDiv.length === 0){
        $modalDiv = $('<div id="hawcModal" class="modal hide fade" tabindex="-1" role="dialog" data-backdrop="static"></div>')
            .append('<div class="modal-header"></div>')
            .append('<div class="modal-body"></div>')
            .append('<div class="modal-footer"></div>')
            .appendTo($('body'));
        $(window).on('resize', $.proxy(this._resizeModal, this));
    }
    this.$modalDiv = $modalDiv;
};
HAWCModal.prototype = {
    show: function(options){
        this.fixedSize = options && options.fixedSize || false;
        this.maxWidth = options && options.maxWidth || Infinity;
        this.maxHeight = options && options.maxHeight || Infinity;
        this._resizeModal();
        this.getBody().scrollTop(0);
        this.$modalDiv.modal('show');
        return this;
    }, hide: function(){
        this.$modalDiv.modal('hide');
        return this;
    }, addHeader: function(html, options){
        var noClose = (options && options.noClose) || false,
            $el = this.$modalDiv.find(".modal-header");
        $el.html(html);
        if (!noClose) $el.prepend('<button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button>');
        return this;
    }, addFooter: function(html, options){
        var noClose = (options && options.noClose) || false,
            $el = this.$modalDiv.find(".modal-footer");
        $el.html(html);
        if (!noClose) $el.append('<button class="btn" data-dismiss="modal">Close</button>');
        return this;
    }, getBody: function(){
        return this.$modalDiv.find(".modal-body");
    }, addBody: function(html){
        this.getBody().html(html).scrollTop(0);
        return this;
    }, _resizeModal: function(){
        var h = parseInt($(window).height(), 10),
            w = parseInt($(window).width(), 10),
            modalCSS = {
                "width": "",
                "max-height": "",
                "height": "",
                "top": "",
                "left": "",
                "margin": ""
            },
            modalBodyCSS = {
                "max-height": ""
            };

        if(!this.fixedSize){
            var mWidth = Math.min(w-50, this.maxWidth),
                mWidthPadding = parseInt((w-mWidth)*0.5, 10),
                mHeight = Math.min(h-50, this.maxHeight);
            _.extend(modalCSS, {
                "width": "{0}px".printf(mWidth),
                "max-height": "{0}px".printf(mHeight),
                "top": "25px",
                "left": "{0}px".printf(mWidthPadding),
                "margin": "0px"
            });
            _.extend(modalBodyCSS, {
                "max-height": "{0}px".printf(mHeight-150)
            });
        }
        this.$modalDiv.css(modalCSS);
        this.getBody().css(modalBodyCSS);
    }, getModal: function(){
        return this.$modalDiv;
    }
};


// Methods for attaching footnotes to any table
var TableFootnotes = function(){
    this.reset();
};
TableFootnotes.prototype = {
    reset: function(){
        this.footnote_number = 97; // start at a
        this.footnotes = [];
    }, add_footnote: function(texts){
        // add a footnote and return the subscript for the footnote
        var keys = [],
            self = this;
        if (!(texts instanceof Array))
            texts = [texts];
        texts.forEach(function(text){
            var key;
            self.footnotes.forEach(function(v){
                if(text === v.text){key = v.key; return;}
            });
            if (key === undefined){
                key = String.fromCharCode(self.footnote_number);
                self.footnotes.push({key: key , text: text});
                self.footnote_number += 1;
            }
            keys.push(key);
        });
        return "<sup>{0}</sup>".printf(keys.join(','));
    }, html_list: function(){
        // return an html formatted list of footnotes
        var list = [];
        this.footnotes.forEach(function(v, i){
            list.push("<sup>{0}</sup> {1}".printf(v.key, v.text));
        });
        return list;
    }
};


// Method for creating a table for descriptive information
var DescriptiveTable = function(){
    this._tbl = $('<table class="table table-condensed table-striped">');
    this._colgroup = $('<colgroup>')
            .append('<col style="width: 30%;"><col style="width: 70%;">');
    this._tbody = $('<tbody>');
    this._tbl.append(this._colgroup, this._tbody);
    return this;
};
DescriptiveTable.prototype = {
    add_tbody_tr: function(description, value, opts){
        opts = opts || {};
        if(value){
            if (parseFloat(value, 10) === value) value = value.toLocaleString();
            if(opts.calculated){value="[{0}]".printf(value);}  // [] = estimated
            var td = $("<td>").html(value);
            if(opts.annotate){
                td.append('<br>', $('<span class="muted">').text(opts.annotate));
            }
            this._tbody.append($('<tr>').append($("<th>").html(description))
                                             .append(td));
        }
        return this;
    }, add_tbody_tr_list: function(description, list_items){
        if(list_items.length>0){
            var ul = $('<ul>').append(
                        list_items.map(function(v){return $('<li>').html(v); })),
                tr = $('<tr>')
                        .append('<th>{0}</th>'.printf(description))
                        .append($('<td>').append(ul));

            this._tbody.append(tr);
        }
        return this;
    }, get_tbl: function(){
        return this._tbl;
    }, get_tbody: function(){
        return this._tbody;
    }
};


// General object for creating any table
var BaseTable = function(){
    this.tbl = $('<table class="table table-condensed table-striped">');
    this.thead = $('<thead>');
    this.colgroup = $('<colgroup>');
    this.tbody = $('<tbody>');
    this.tfoot = $('<tfoot>');
    this.footnotes  = new TableFootnotes();
    this.tbl.append(this.colgroup, this.thead, this.tfoot, this.tbody);
};
BaseTable.prototype = {
    getTbl: function(){
        this._set_footnotes();
        return this.tbl;
    }, numCols: function(cols){
        if(cols){
            this._numCols = cols;
        } else if(this._numCols === undefined){
            this._numCols = this.thead.first().children().first().children().length;
        }
        return this._numCols;
    }, addHeaderRow: function(val){
        this.addRow(val, true);
    }, addRow: function(val, isHeader){
        var tr,
            tagName = (isHeader) ? "<th>" : "<td>";
        if(val instanceof Array){
            tr = $('<tr>');
            val.forEach(function(v){tr.append($(tagName).html(v));});
        } else if (val instanceof jQuery && val.first().prop('tagName') === "TR") {
            tr = val;
        } else {
            console.log('unknown input type');
        }
        if(isHeader){
            this.thead.append(tr);
        } else {
            this.tbody.append(tr);
        }
        return tr;
    }, setColGroup: function(percents){
        this.colgroup.html(percents.map(function(v){
            return '<col style="width: {0}%;">'.printf(v);
        }));
    }, _set_footnotes: function(){
        var txt = this.footnotes.html_list().join('<br>'),
            colspan = this.numCols();
        this.tfoot.html('<tr><td colspan="{0}">{1}</td></tr>'.printf(colspan, txt));
    }
};
