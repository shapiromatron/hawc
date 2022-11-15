import PropTypes from "prop-types";
import React, {Component} from "react";
import h from "shared/utils/helpers";

import HelpText from "./HelpText";
import LabelInput from "./LabelInput";

class FileInput extends Component {
    render() {
        const fieldId = h.randomString(),
            {label, helpText, value, onChange} = this.props;
        return (
            <div className="form-group">
                {label ? <LabelInput for={`#${fieldId}`} label={label} /> : null}
                <input
                    className="form-control-file"
                    type="file"
                    id={fieldId}
                    value={value}
                    onChange={e => onChange(e.target.files[0])}
                />
                {helpText ? <HelpText text={helpText} /> : null}
            </div>
        );
    }
}

FileInput.propTypes = {
    helpText: PropTypes.string,
    label: PropTypes.string,
    onChange: PropTypes.func.isRequired,
    value: PropTypes.string,
};

export default FileInput;
