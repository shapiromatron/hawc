import shared from 'shared/utils/helpers';

var helpers = Object.assign({}, shared, {
    sortDates(objects, field, order){
        return objects.sort((a, b) => {
            let dateA = a[field] ? new Date(a[field]) : 0,
                dateB = b[field] ? new Date(b[field]) : 0;
            if (dateA > dateB) return 1;
            if (dateA < dateB) return -1;
            return 0;
        });
    },
    sortStrings(objects, field){
        return objects.sort((a, b) => {
            if (a[field].toLowerCase() > b[field].toLowerCase()) return 1;
            if (a[field].toLowerCase() < b[field].toLowerCase()) return -1;
            return 0;
        });
    },
});

export default helpers;
