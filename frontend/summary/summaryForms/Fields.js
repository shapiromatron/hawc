import HAWCUtils from "shared/utils/HAWCUtils";

import $ from "$";

class InputField {
    constructor(schema, $parent, parent) {
        this.$parent = $parent;
        this.schema = schema;
        this.parent = parent;
        return this;
    }

    toSerialized() {
        return HAWCUtils.abstractMethod();
    }

    fromSerialized() {
        return HAWCUtils.abstractMethod();
    }

    render() {
        return HAWCUtils.abstractMethod();
    }
}

class TextField extends InputField {
    toSerialized() {
        this.parent.settings[this.schema.name] = this.$inp.val();
    }

    fromSerialized() {
        this.$inp.val(this.parent.settings[this.schema.name]);
    }

    _setInput() {
        this.$inp = $(
            `<input type="text" name="${this.schema.name}" class="form-control" required>`
        );
    }

    render() {
        this._setInput();
        var $div = $('<div class="form-group">').append(this.$inp);

        if (this.schema.label)
            $div.prepend(`<label class="col-form-label">${this.schema.label}</label>`);

        if (this.schema.helpText)
            $div.append(`<span class="form-text text-muted">${this.schema.helpText}</span>`);

        this.$parent.append($div);
    }
}

class IntegerField extends TextField {
    toSerialized() {
        this.parent.settings[this.schema.name] = parseInt(this.$inp.val(), 10);
    }

    _setInput() {
        this.$inp = $(
            `<input type="number" name="${this.schema.name}" class="form-control" required>`
        );
    }
}

class FloatField extends TextField {
    toSerialized() {
        this.parent.settings[this.schema.name] = parseFloat(this.$inp.val(), 10);
    }

    _setInput() {
        this.$inp = $(
            `<input type="number" step="any" name="${this.schema.name}" class="form-control" required>`
        );
    }
}

class ColorField extends TextField {
    _setInput() {
        this.$inp = $(
            `<input type="color" name="${this.schema.name}" class="form-control" required>`
        );
    }
}

class CheckboxField extends TextField {
    toSerialized() {
        this.parent.settings[this.schema.name] = this.$inp.prop("checked");
    }

    fromSerialized() {
        this.$inp.prop("checked", this.parent.settings[this.schema.name]);
    }

    _setInput() {
        this.$inp = $(
            `<input type="checkbox" class="form-check-input" name="${this.schema.name}">`
        );
    }

    render() {
        this._setInput();
        var $div = $('<div class="form-group form-check">')
            .append(this.$inp)
            .append(`<label class="form-check-label">${this.schema.label}:</label>`);

        if (this.schema.helpText)
            $div.append(`<span class="form-text text-muted">${this.schema.helpText}</span>`);

        this.$parent.append($div);
    }
}

class RadioField extends TextField {
    toSerialized() {
        var sel = `input[name="${this.schema.name}"]:checked`;
        this.parent.settings[this.schema.name] = this.$inp.find(sel).val();
    }

    fromSerialized() {
        var sel = `input[value="${this.parent.settings[this.schema.name]}"]`;
        this.$inp.find(sel).prop("checked", true);
    }

    _setInput() {
        var radios = this.schema.options.map(d => {
            return `<div class='form-check'>
                <input name="${this.schema.name}" type="radio" class="form-check-input" value="${d.value}">
                <label class="form-check-label">${d.label}</label>
            </div>`;
        });
        this.$inp = $("<div>").html(radios.join("\n"));
    }

    render() {
        this._setInput();
        var $div = $('<div class="form-group">').append(this.$inp);

        if (this.schema.helpText)
            $div.append(`<span class="form-text text-muted">${this.schema.helpText}</span>`);

        this.$parent.append($div);
    }
}

class SelectField extends TextField {
    _setInput() {
        var makeOpt = function (d) {
            return `<option value="${d[0]}">${d[1]}</option>`;
        };
        this.$inp = $(`<select name="${this.schema.name}" class="form-control">`).html(
            this.schema.opts.map(makeOpt).join("")
        );
    }
}

class NullField extends InputField {
    toSerialized() {}

    fromSerialized() {}
}

class SpacerNullField extends NullField {
    render() {
        this.$parent.append("<hr>");
    }
}

class HeaderNullField extends NullField {
    render() {
        this.$parent.append($("<h4>").text(this.schema.label));
    }
}

class HelpTextNullField extends NullField {
    render() {
        this.$parent.append(
            `<p class="helpTextForTable form-text text-muted pb-2">${this.schema.helpText}</p>`
        );
    }
}

export {InputField};
export {TextField};
export {IntegerField};
export {FloatField};
export {ColorField};
export {CheckboxField};
export {RadioField};
export {SelectField};
export {NullField};
export {SpacerNullField};
export {HeaderNullField};
export {HelpTextNullField};
