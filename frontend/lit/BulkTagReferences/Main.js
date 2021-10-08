import React, {Component} from "react";
import PropTypes from "prop-types";
import {inject, observer} from "mobx-react";
import _ from "lodash";

import SelectInput from "shared/components/SelectInput";

@inject("store")
@observer
class BulkTagReferencesMain extends Component {
    render() {
        const {store} = this.props,
            {handleFileInput} = store;
        return (
            <div>
                <button onClick={store.getReferences}>Get references</button>
                <br />
                <button onClick={store.getTags}>Get tags</button>
                <br />
                <input id="fileItem" type="file" onChange={handleFileInput} />
                <br />
                {store.datasetColumnChoices.length ? (
                    <SelectInput
                        choices={store.datasetColumnChoices}
                        multiple={false}
                        handleSelect={v => store.setDatasetIdColumn(v)}
                        value={store.datasetIdColumn}
                        label="Select ID column"
                    />
                ) : null}
                <br />
                <SelectInput
                    choices={store.referenceColumnChoices}
                    multiple={false}
                    handleSelect={v => store.setReferenceIdColumn(v)}
                    value={store.referenceIdColumn}
                    label="Select ID column type"
                />
                <br />
                {store.datasetColumnChoices.length ? (
                    <SelectInput
                        choices={store.datasetColumnChoices}
                        multiple={false}
                        handleSelect={v => store.setDatasetTagColumn(v)}
                        value={store.datasetTagColumn}
                        label="Select tag column"
                    />
                ) : null}
                <br />
                Map tag value to HAWC tag
                <br />
                <button onClick={store.createDatasetTag}>Add</button>
                <br />
                {store.datasetTags.map((v, i) => (
                    <div key={`div-${i}`}>
                        <select onChange={e => store.setDatasetTagLabel(i, e.target.value)}>
                            {_.map(store.datasetTagChoices, (c, j) => (
                                <option key={`option-${i}-${j}`} value={c.id}>
                                    {c.label}
                                </option>
                            ))}
                        </select>
                        <select onChange={e => store.setDatasetTagId(i, e.target.value)}>
                            {_.map(store.HAWCTagChoices, (c, j) => (
                                <option key={`option-${i}-${j}`} value={c.id}>
                                    {c.label}
                                </option>
                            ))}
                        </select>
                        <button onClick={() => store.deleteDatasetTag(i)}>Delete</button>
                    </div>
                ))}
                <br />
                {JSON.stringify(store.datasetFinal)}
                <br />
                <button onClick={store.bulkUpdateTags}>Submit</button>
            </div>
        );
    }
}

BulkTagReferencesMain.propTypes = {
    store: PropTypes.object,
};

export default BulkTagReferencesMain;
