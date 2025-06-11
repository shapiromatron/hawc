import {Provider} from "mobx-react";
import React from "react";
import ReactDOM from "react-dom";
import BulkTagReferencesMain from "./BulkTagReferences/Main";
import BulkTagReferencesMainStore from "./BulkTagReferences/store";
import Reference from "./Reference";
import ReferenceTreeMain from "./ReferenceTreeBrowse/Main";
import ReferenceTreeMainStore from "./ReferenceTreeBrowse/store";
import TagReferencesMain from "./TagReferences/Main";
import TagReferencesMainStore from "./TagReferences/store";
import TagTree from "./TagTree";
import TagTreeViz from "./TagTreeViz";
import ReferenceComponent from "./components/Reference";
import ReferenceTable from "./components/ReferenceTable";
import Venn from "./components/Venn";

export default {
    TagTree,
    startupReferenceTable(el, config) {
        let tagtree = new TagTree(config.tags[0]),
            references = Reference.array(config.references, tagtree, false);
        ReactDOM.render(
            <ReferenceTable
                references={references}
                showActions={false}
                tagUDFContents={config.tag_binding_contents}
            />,
            el
        );
    },
    startupReferenceDetail(el, config) {
        let tagtree = new TagTree(config.tags[0]),
            ref = new Reference(config.reference, tagtree),
            options = {
                showActions: config.canEdit,
                actionsBtnClassName: "btn-primary",
                expanded: true,
                tagUDFContents: config.tag_binding_contents,
            };

        ReactDOM.render(<ReferenceComponent reference={ref} {...options} />, el);
    },
    startupReferenceList(el, config) {
        ReactDOM.render(
            <Provider store={new ReferenceTreeMainStore(config)}>
                <ReferenceTreeMain />
            </Provider>,
            el
        );
    },
    startupTagReferences(el, config) {
        ReactDOM.render(
            <Provider store={new TagReferencesMainStore(config)}>
                <TagReferencesMain />
            </Provider>,
            el
        );
    },
    startupBulkTagReferences(el, config) {
        ReactDOM.render(
            <Provider store={new BulkTagReferencesMainStore(config)}>
                <BulkTagReferencesMain />
            </Provider>,
            el
        );
    },
    startupTagTreeViz(el, config) {
        let tagtree = new TagTree(config.tags[0], config.assessment_id, config.search_id),
            settings = {
                hide_empty_tag_nodes: false,
                width: 1280,
                height: 800,
                can_edit: config.can_edit,
                show_legend: true,
                show_counts: true,
            };
        tagtree.rename_top_level_node(config.assessment_name);
        tagtree.add_references(config.references);
        new TagTreeViz(tagtree, el, config.title, settings);
    },
    startupVenn(el, config) {
        ReactDOM.render(<Venn data={config} />, el);
    },
};
