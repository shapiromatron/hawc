import React from "react";
import { EditableRow } from "shared/components/EditableRowData";
import IntegerInput from "shared/components/IntegerInput";
import TextInput from "shared/components/TextInput";
import wrapRow from "shared/components/WrapRow";

class PrismaEditableRow extends EditableRow {
    constructor(props) {
        super(props);
        this.state = { edit: props.initiallyEditable, edit_styles: props.editStyles };
    }

    renderStyleOptions(key, row, index) {
        const { changeStylingSettings } = this.props.store.subclass;
        return (
            <div>
                {wrapRow([
                    <IntegerInput
                        name={`${key}-width-${index}`}
                        onChange={e => changeStylingSettings(key, index, "width", parseInt(e.target.value))}
                        label="Width"
                        value={row.styling.width}
                        helpText="Set the width of this element. When 0 is entered, this will be calculated automatically."
                    />,
                    <IntegerInput
                        name={`${key}-height-${index}`}
                        value={row.styling.height}
                        label="Height"
                        onChange={e => changeStylingSettings(key, index, "height", parseInt(e.target.value))}
                        helpText="Set the height of this element. When 0 is entered, this will be calculated automatically."
                    />,
                    <IntegerInput
                        name={`${key}-border-width-${index}`}
                        value={row.styling.stroke_width}
                        label="Stroke Width"
                        onChange={e =>
                            changeStylingSettings(key, index, "stroke_width", parseInt(e.target.value))
                        }
                        helpText="Set the width of the border. Set to 0 for no border."
                    />,
                    <IntegerInput
                        name={`${key}-stroke-radius-${index}`}
                        value={row.styling.stroke_radius}
                        label="Stroke Radius"
                        onChange={e =>
                            changeStylingSettings(key, index, "stroke_radius", parseInt(e.target.value))
                        }
                        helpText="Set the roundness of the corners."
                    />,
                    <TextInput
                        name={`${key}-stroke-color-${index}`}
                        value={row.styling.stroke_color}
                        label="Stroke Color"
                        onChange={e =>
                            changeStylingSettings(key, index, "stroke_color", e.target.value)
                        }
                        type="color"
                        helpText="Set the color of the border."
                    />,
                    <TextInput
                        name={`${key}-bg-color-${index}`}
                        value={row.styling.bg_color}
                        label="Background Color"
                        onChange={e => changeStylingSettings(key, index, "bg_color", e.target.value)}
                        type="color"
                    />,
                    <TextInput
                        name={`${key}-font-color-${index}`}
                        value={row.styling.font_color}
                        label="Font Color"
                        onChange={e => changeStylingSettings(key, index, "font_color", e.target.value)}
                        type="color"
                    />,
                    <IntegerInput
                        name={`${key}-padding-x-${index}`}
                        value={row.styling.padding_x}
                        label="Text Padding (X axis)"
                        onChange={e => changeStylingSettings(key, index, "padding_x", parseInt(e.target.value))}
                        helpText="Sets the padding space to the left and right of text elements"
                    />,
                    <IntegerInput
                        name={`${key}-padding-y-${index}`}
                        value={row.styling.padding_y}
                        label="Text Padding (Y axis)"
                        onChange={e => changeStylingSettings(key, index, "padding_y", parseInt(e.target.value))}
                        helpText="Sets the padding space above and below text elements"
                    />,
                    <IntegerInput
                        name={`${key}-x-${index}`}
                        value={row.styling.x}
                        label="Adjust X position"
                        onChange={e => changeStylingSettings(key, index, "x", parseInt(e.target.value))}
                    />,
                    <IntegerInput
                        name={`${key}-y-${index}`}
                        value={row.styling.y}
                        label="Adjust Y position"
                        onChange={e => changeStylingSettings(key, index, "y", parseInt(e.target.value))}
                    />
                ], "form-row"
                )}
            </div>
        );
    }
}

export { PrismaEditableRow };
