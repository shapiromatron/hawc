import React from "react";
import {EditableRow} from "shared/components/EditableRowData";
import FloatInput from "shared/components/FloatInput";
import IntegerInput from "shared/components/IntegerInput";
import TextInput from "shared/components/TextInput";

class PrismaEditableRow extends EditableRow {
    constructor(props) {
        super(props);
        this.state = {edit: props.initiallyEditable, edit_styles: props.editStyles};
    }

    renderStyleOptions(key, row, index) {
        const {changeStylingSettings} = this.props.store.subclass;
        return (
            <div className="form-row">
                <IntegerInput
                    name={`${key}-width-${index}`}
                    onChange={e => changeStylingSettings(key, index, "width", e.target.value)}
                    label="Width"
                    value={row.styling.width}
                />
                <IntegerInput
                    name={`${key}-height-${index}`}
                    value={row.styling.height}
                    label="Height"
                    onChange={e => changeStylingSettings(key, index, "height", e.target.value)}
                />
                <IntegerInput
                    name={`${key}-border-width-${index}`}
                    value={row.styling.border_width}
                    label="Border Width"
                    onChange={e =>
                        changeStylingSettings(key, index, "border_width", e.target.value)
                    }
                />
                <IntegerInput
                    name={`${key}-stroke-radius-${index}`}
                    value={row.styling.stroke_radius}
                    label="Stroke Radius"
                    onChange={e =>
                        changeStylingSettings(key, index, "stroke_radius", e.target.value)
                    }
                />
                <TextInput
                    name={`${key}-bg-color-${index}`}
                    value={row.styling.bg_color}
                    label="Background Color"
                    onChange={e => changeStylingSettings(key, index, "bg_color", e.target.value)}
                    type="color"
                />
                <TextInput
                    name={`${key}-border-color-${index}`}
                    value={row.styling.border_color}
                    label="Border Color"
                    onChange={e =>
                        changeStylingSettings(key, index, "border_color", e.target.value)
                    }
                    type="color"
                />
                <TextInput
                    name={`${key}-font-color-${index}`}
                    value={row.styling.font_color}
                    label="Font Color"
                    onChange={e => changeStylingSettings(key, index, "font_color", e.target.value)}
                    type="color"
                />
                <FloatInput
                    name={`${key}-font-size-${index}`}
                    value={row.styling.font_size}
                    label="Font size"
                    onChange={e => changeStylingSettings(key, index, "font_size", e.target.value)}
                />
                <IntegerInput
                    name={`${key}-padding-x-${index}`}
                    value={row.styling.padding_x}
                    label="Padding X"
                    onChange={e => changeStylingSettings(key, index, "padding_x", e.target.value)}
                />
                <IntegerInput
                    name={`${key}-padding-y-${index}`}
                    value={row.styling.padding_y}
                    label="Padding Y"
                    onChange={e => changeStylingSettings(key, index, "padding_y", e.target.value)}
                />
                <IntegerInput
                    name={`${key}-x-${index}`}
                    value={row.styling.x}
                    label="Adjust X position"
                    onChange={e => changeStylingSettings(key, index, "x", e.target.value)}
                />
                <IntegerInput
                    name={`${key}-y-${index}`}
                    value={row.styling.y}
                    label="Adjust Y position"
                    onChange={e => changeStylingSettings(key, index, "y", e.target.value)}
                />
            </div>
        );
    }
}

export {PrismaEditableRow};
