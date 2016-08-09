let header_cw = {
        'Extra': '%',
        'Added': '% AR',
        'Abs. Dev.': 'AD',
        'Std. Dev.': 'SD',
        'Rel. Dev.': '% RD',
        'Point': 'Pt',
    },
    asLabel = function(d){
        let str, val;
        switch(d.type){
        case 'Extra':
        case 'Added':
        case 'Rel. Dev.':
            str = header_cw[d.type];
            val = d.value*100;
            break;
        case 'Abs. Dev.':
        case 'Std. Dev.':
        case 'Point':
            str = header_cw[d.type];
            val = d.value;
            break;
        default:
            str = d.type;
            val = d.value;
        }
        return `${val}${str}`;
    };

export { asLabel };


