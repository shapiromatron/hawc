import {computed, observable, toJS} from "mobx";
import HAWCModal from "shared/utils/HAWCModal";
import h from "shared/utils/helpers";

class PrismaDatastore {
    // Store that is connected to the Prisma plot
    @observable dataset = null;
    @observable settings = null;
    @observable objects = null;

    constructor(settings, dataset) {
        this.settings = settings;
        this.dataset = dataset;
        this.setup_objects();
        this.modal = new HAWCModal();
    }

    setup_objects() {}

    @computed get settingsHash() {
        return h.hashString(JSON.stringify(this.settings));
    }

    @computed get getDiagramSections() {
        return [
            {
                label: "Records",
                key: "Records",
                block_layout: "card",
                styling: {
                    width: this.MAX_WIDTH * 2 + this.SPACING_H + 30,
                },
                blocks: [
                    {
                        label: "Source 1",
                        key: "Source 1",
                        value: "",
                        styling: {"text-color": "red", width: "200"},
                    },
                    {
                        label: "Source 2",
                        key: "Source 2",
                        value: "",
                    },
                    {
                        label: "Source 3",
                        key: "Source 3",
                        value: "",
                    },
                    {
                        label: "Source 4",
                        key: "Source 4",
                        value: "",
                    },
                    {
                        label: "Source 5",
                        key: "Source 5",
                        value: "",
                    },
                    {
                        label: "Source 6",
                        key: "Source 6",
                        value: "",
                    },
                    {
                        label: "Source 7",
                        key: "Source 7",
                        value: "",
                    },
                    {
                        label: "Source 8",
                        key: "Source 8",
                        value: "",
                    },
                    {
                        label: "Source 9",
                        key: "Source 9",
                        value: "",
                    },
                    /*
                    {
                        "label": "References identified",
                        "tags": ["Included", "Excluded"],
                        "count": "unique_sum",
                        "value": 13725,
                        "refs": '[...]',
                    }*/
                ],
            },
            {
                label: "TIAB",
                key: "TIAB",
                blocks: [
                    {
                        label: "References screened",
                        key: "References screened",
                        tags: [
                            "Included",
                            "Excluded|Manually excluded in Distiller (full-text)",
                            "Excluded|Manually excluded in SWIFT-Review",
                            "Excluded|Automatically excluded via ML in SWIFT-Active Screener",
                            "Excluded|Manually excluded in Distiller (TIAB)",
                        ],
                        count: "unique_sum",
                        value: 13725,
                        refs: "[...]",
                    },
                    {
                        label: "References excluded",
                        key: "References excluded",
                        tags: [
                            "Excluded|Manually excluded in SWIFT-Review",
                            "Excluded|Automatically excluded via ML in SWIFT-Active Screener",
                            "Excluded|Manually excluded in Distiller (TIAB)",
                        ],
                        count: "unique_sum",
                        value: 13189,
                        refs: "[...]",
                        styling: {
                            y: "-30",
                            x: "-50",
                        },
                    },
                ],
            },
            {
                label: "FT",
                key: "FT",
                blocks: [
                    {
                        label: "References screened",
                        key: "References screened",
                        tags: ["Included", "Excluded|Manually excluded in Distiller (full-text)"],
                        count: "unique_sum",
                        value: 541,
                        refs: "[...]",
                    },
                    {
                        label: "References excluded",
                        key: "References excluded",
                        tags: [
                            "Excluded|Manually excluded in Distiller (full-text)|Unable to obtain full-text",
                        ],
                        count: "unique_sum",
                        value: 32,
                        refs: "[...]",
                    },
                ],
            },
            {
                label: "FT - eligible",
                key: "FT - eligible",
                styling: {
                    "bg-color": "grey",
                    "text-padding-x": "315",
                    "text-padding-y": "20",
                    "text-size": ".3",
                    "text-style": "bold",
                },
                blocks: [
                    {
                        label: "References screened",
                        key: "References screened",
                        tags: [
                            "Included",
                            "Excluded|Manually excluded in Distiller (full-text)|No data provided",
                            "Excluded|Manually excluded in Distiller (full-text)|No relevant exposure",
                            "Excluded|Manually excluded in Distiller (full-text)|Wildlife study",
                        ],
                        count: "unique_sum",
                        value: 509,
                        refs: "[...]",
                        styling: {
                            "text-color": "white",
                            "bg-color": "green",
                            stroke: "blue",
                            "stroke-width": "10",
                            rx: "0",
                            ry: "0",
                        },
                    },
                    {
                        label: "References excluded",
                        key: "References excluded",
                        block_layout: "list",
                        styling: {
                            height: this.MIN_HEIGHT,
                        },
                        sub_blocks: [
                            {
                                label: "No data provided",
                                key: "No data provided",
                                tags: [
                                    "Excluded|Manually excluded in Distiller (full-text)|No data provided",
                                ],
                                count: "unique_sum",
                                value: 4,
                                refs: "[...]",
                                styling: {"text-color": "red"},
                            },
                            {
                                label: "No relevant exposure",
                                key: "No relevant exposure",
                                tags: [
                                    "Excluded|Manually excluded in Distiller (full-text)|No relevant exposure",
                                ],
                                count: "unique_sum",
                                value: 146,
                                refs: "[...]",
                            },
                            {
                                label: "Wildlife study",
                                key: "Wildlife study",
                                tags: [
                                    "Excluded|Manually excluded in Distiller (full-text)|Wildlife study",
                                ],
                                count: "unique_sum",
                                value: 4,
                                refs: "[...]",
                            },
                        ],
                        count: "unique_sum",
                        value: 150,
                        refs: "[...]",
                    },
                ],
            },
            {
                label: "Included studies",
                key: "Included studies",
                blocks: [
                    {
                        label: "Results",
                        key: "Results",
                        tags: ["Included"],
                        count: "unique_sum",
                        value: 359,
                        refs: "[...]",
                    },
                ],
            },
        ];
    }

    @computed get getConnections() {
        return [
            {
                src: "Records",
                dst: "TIAB",
                styling: {
                    "arrow-type": "11",
                },
            },
            {
                src: "TIAB.References screened",
                dst: "TIAB.References excluded",
            },
            {
                src: "TIAB.References screened",
                dst: "FT.References excluded",
                styling: {
                    "arrow-force-vertical": "true",
                },
            },
            {
                src: "TIAB.References screened",
                dst: "FT.References screened",
                styling: {
                    "arrow-color": "blue",
                    "arrow-width": "6",
                },
            },
            {
                src: "FT.References screened",
                dst: "FT - eligible.References screened",
            },
            {
                src: "FT - eligible.References screened",
                dst: "FT - eligible.References excluded",
            },
            {
                src: "FT - eligible.References screened",
                dst: "Included studies.Results",
            },
        ];
    }

    @computed get getFilterHash() {
        return h.hashString(JSON.stringify(toJS(this.filterWidgetState)));
    }
}

export default PrismaDatastore;
