export const datasetTypes = {
        DATASET: "dataset",
        BIOASSAY: "bioassay",
        EPI: "epi",
        LITERATURE_TAGS: "literature tags",
    },
    plotStyles = {
        HEATMAP: "heatmap",
        BUBBLE_PLOT: "bubbleplot",
    },
    getDefaultFilter = function() {
        return {};
    },
    getDefaultAxes = function() {
        return {};
    },
    getDefaultSettings = function() {
        return {
            dataset_type: datasetTypes.DATASET,
            data_url: "",
            title: {
                text: "",
                x: 0,
                y: 0,
                rotation: "",
            },
            x_label: {
                text: 0,
                x: 0,
                y: 0,
                rotation: 0,
            },
            y_label: {
                text: 0,
                x: 0,
                y: 0,
                rotation: 0,
            },
            x_axes: [],
            y_axes: [],
            plot_style: plotStyles.HEATMAP,
            cell_on_click: "",
            cell_on_ctrl_click: "",
            filters: [],
        };
    };
