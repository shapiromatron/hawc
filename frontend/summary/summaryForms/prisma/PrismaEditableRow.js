import React from "react";
import {EditableRow} from "shared/components/EditableRowData";
import IntegerInput from "shared/components/IntegerInput";
import TextInput from "shared/components/TextInput";
import wrapRow from "shared/components/WrapRow";

class PrismaEditableRow extends EditableRow {
    constructor(props) {
        super(props);
        this.state = {edit: props.initiallyEditable, edit_styles: props.editStyles};
    }

    renderStyleOptions(key, row, index) {
        const {changeStylingSettings} = this.props.store.subclass;
        return (
            <>
                {wrapRow(
                    [
                        <IntegerInput
                            key={`${key}-width-${index}`}
                            name={`${key}-width-${index}`}
                            onChange={e =>
                                changeStylingSettings(key, index, "width", parseInt(e.target.value))
                            }
                            label="Width"
                            value={row.styles.width}
                            helpText="Set the width of this element. When 0 is entered, this will be calculated automatically"
                        />,
                        <IntegerInput
                            key={`${key}-height-${index}`}
                            name={`${key}-height-${index}`}
                            value={row.styles.height}
                            label="Height"
                            onChange={e =>
                                changeStylingSettings(
                                    key,
                                    index,
                                    "height",
                                    parseInt(e.target.value)
                                )
                            }
                            helpText="Set the height of this element. When 0 is entered, this will be calculated automatically"
                        />,
                        <IntegerInput
                            key={`${key}-border_radius-${index}`}
                            name={`${key}-border_radius-${index}`}
                            value={row.styles.border_radius}
                            label="Border Rounding"
                            onChange={e =>
                                changeStylingSettings(
                                    key,
                                    index,
                                    "border_radius",
                                    parseInt(e.target.value)
                                )
                            }
                            helpText="Set the roundness of the corners"
                        />,
                        <IntegerInput
                            key={`${key}-border_width-${index}`}
                            name={`${key}-border_width-${index}`}
                            value={row.styles.border_width}
                            label="Border Width"
                            onChange={e =>
                                changeStylingSettings(
                                    key,
                                    index,
                                    "border_width",
                                    parseInt(e.target.value)
                                )
                            }
                            helpText="Set the width of the border. Set to 0 for no border"
                        />,
                        <TextInput
                            key={`${key}-border_color-${index}`}
                            name={`${key}-border_color-${index}`}
                            value={row.styles.border_color}
                            label="Border Color"
                            onChange={e =>
                                changeStylingSettings(key, index, "border_color", e.target.value)
                            }
                            type="color"
                            helpText="Set the color of the border"
                        />,
                        <TextInput
                            key={`${key}-bg-color-${index}`}
                            name={`${key}-bg-color-${index}`}
                            value={row.styles.bg_color}
                            label="Background Color"
                            onChange={e =>
                                changeStylingSettings(key, index, "bg_color", e.target.value)
                            }
                            type="color"
                        />,
                        <IntegerInput
                            key={`${key}-padding-x-${index}`}
                            name={`${key}-padding-x-${index}`}
                            value={row.styles.padding_x}
                            label="Text Padding (X axis)"
                            onChange={e =>
                                changeStylingSettings(
                                    key,
                                    index,
                                    "padding_x",
                                    parseInt(e.target.value)
                                )
                            }
                            helpText="Sets the padding space to the left and right of text elements"
                        />,
                        <IntegerInput
                            key={`${key}-padding-y-${index}`}
                            name={`${key}-padding-y-${index}`}
                            value={row.styles.padding_y}
                            label="Text Padding (Y axis)"
                            onChange={e =>
                                changeStylingSettings(
                                    key,
                                    index,
                                    "padding_y",
                                    parseInt(e.target.value)
                                )
                            }
                            helpText="Sets the padding space above and below text elements"
                        />,
                        <IntegerInput
                            key={`${key}-x-${index}`}
                            name={`${key}-x-${index}`}
                            value={row.styles.x}
                            label="Adjust X position"
                            onChange={e =>
                                changeStylingSettings(key, index, "x", parseInt(e.target.value))
                            }
                        />,
                        <IntegerInput
                            key={`${key}-y-${index}`}
                            name={`${key}-y-${index}`}
                            value={row.styles.y}
                            label="Adjust Y position"
                            onChange={e =>
                                changeStylingSettings(key, index, "y", parseInt(e.target.value))
                            }
                        />,
                    ],
                    "form-row"
                )}
            </>
        );
    }
}

export {PrismaEditableRow};
