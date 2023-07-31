class FilterBase {
    constructor(field, values) {
        this.field = field;
        this.values = values;
    }
    filter(data) {
        throw Error("Not implemented");
    }
    isEmpty() {
        throw Error("Not implemented");
    }
}

class IntegerRangeFilter extends FilterBase {
    filter(data) {
        const min = this.values.min === null ? -Infinity : this.values.min,
            max = this.values.max === null ? Infinity : this.values.max;
        return data.filter(item => item[this.field] >= min && item[this.field] <= max);
    }
    isEmpty() {
        return this.values.min === null && this.values.max === null;
    }
}

class StringContainsFilter extends FilterBase {
    filter(data) {
        const values = new Set(this.values);
        return data.filter(item => values.has(item[this.field]));
    }
    isEmpty() {
        return this.values.length === 0;
    }
}

export {IntegerRangeFilter, StringContainsFilter};
