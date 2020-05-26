import _ from "lodash";
import $ from "$";

import HAWCUtils from "utils/HAWCUtils";

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
        this.$inp = $(`<input type="text" name="${this.schema.name}" class="span12" required>`);
    }

    render() {
        this._setInput();
        var $ctrl = $('<div class="controls">').append(this.$inp);

        if (this.schema.helpText)
            $ctrl.append(`<span class="help-inline">${this.schema.helpText}</span>`);

        var $div = $('<div class="control-group form-row">')
            .append(`<label class="control-label">${this.schema.label}:</label>`)
            .append($ctrl);

        this.$parent.append($div);
    }
}

class IntegerField extends TextField {
    toSerialized() {
        this.parent.settings[this.schema.name] = parseInt(this.$inp.val(), 10);
    }

    _setInput() {
        this.$inp = $(`<input type="number" name="${this.schema.name}" class="span12" required>`);
    }
}

class FloatField extends TextField {
    toSerialized() {
        this.parent.settings[this.schema.name] = parseFloat(this.$inp.val(), 10);
    }

    _setInput() {
        this.$inp = $(
            `<input type="number" step="any" name="${this.schema.name}" class="span12" required>`
        );
    }
}

class ColorField extends TextField {
    _setInput() {
        this.$inp = $(`<input type="color" name="${this.schema.name}" class="span12" required>`);
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
        this.$inp = $(`<input type="checkbox" name="${this.schema.name}">`);
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
        var radios = _.map(
            this.schema.options,
            _.bind(function(d) {
                return `<label class="radio inline">
                    ${d.label}
                    <input name="${this.schema.name}" type="radio" value="${d.value}">
                </label>`;
            }, this)
        );
        this.$inp = $("<div>").html(radios.join("\n"));
    }
}

class SelectField extends TextField {
    _setInput() {
        var makeOpt = function(d) {
            return `<option value="${d[0]}">${d[1]}</option>`;
        };
        this.$inp = $(`<select name="${this.schema.name}" class="span12">`).html(
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
        this.$parent.append(`<p class="helpTextForTable help-inline">${this.schema.helpText}</p>`);
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
