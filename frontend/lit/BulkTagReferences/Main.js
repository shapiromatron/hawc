import React, {Component} from "react";
import PropTypes from "prop-types";
import {inject, observer} from "mobx-react";
import _ from "lodash";

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
                Pick id column
                <select onChange={e => store.setDatasetIdColumn(e.target.value)}>
                    {_.map(store.datasetColumnChoices, c => (
                        <option value={c[0]}>{c[1]}</option>
                    ))}
                </select>
                <br />
                Pick id column type
                <select onChange={e => store.setReferenceIdColumn(e.target.value)}>
                    {_.map(store.referenceColumnChoices, c => (
                        <option value={c[0]}>{c[1]}</option>
                    ))}
                </select>
                <br />
                Pick tag column
                <select onChange={e => store.setDatasetTagColumn(e.target.value)}>
                    {_.map(store.datasetColumnChoices, c => (
                        <option value={c[0]}>{c[1]}</option>
                    ))}
                </select>
                <br />
                Map tag value to HAWC tag
                <br />
                <button onClick={store.createDatasetTag}>Add</button>
                <br />
                {store.datasetTags.map((v, i) => (
                    <div key={`div-${i}`}>
                        <select onChange={e => store.setDatasetTagLabel(i, e.target.value)}>
                            {_.map(store.datasetTagChoices, (c, j) => (
                                <option key={`option-${i}-${j}`} value={c[0]}>
                                    {c[1]}
                                </option>
                            ))}
                        </select>
                        <select onChange={e => store.setDatasetTagId(i, e.target.value)}>
                            {_.map(store.HAWCTagChoices, (c, j) => (
                                <option key={`option-${i}-${j}`} value={c[0]}>
                                    {c[1]}
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
