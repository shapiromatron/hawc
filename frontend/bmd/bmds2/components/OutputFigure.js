import BmdLine from "bmd/common/BmdLine";
import PropTypes from "prop-types";
import React from "react";

class OutputFigure extends React.Component {
    constructor(props) {
        super(props);
        this.epFigure = React.createRef();
    }

    componentDidMount() {
        let {endpoint} = this.props,
            ept = endpoint.renderPlot($(this.epFigure.current), {showBmd: false});
        ept.setScatter();
        this.plt = ept.scatter;
        this.renderSelectedLine(this.props.selectedModel);
    }

    renderHoverLine(model) {
        if (model === null) {
            if (this.hover_line) {
                this.hover_line.destroy();
                delete this.hover_line;
            }
        } else {
            if (
                model.execution_error ||
                (this.selected_line && model.id == this.selected_line.model.id)
            ) {
                return;
            }

            this.hover_line = new BmdLine(model, this.plt, "red");
            this.hover_line.render();
        }
    }

    renderSelectedLine(model) {
        if (
            model === null ||
            model.execution_error ||
            (this.selected_line && this.selected_line.model.id !== model.id)
        ) {
            if (this.selected_line) {
                this.selected_line.destroy();
                delete this.selected_line;
            }
        }

        if (model !== null) {
            this.selected_line = new BmdLine(model, this.plt, "blue");
            this.selected_line.render();
        }
    }

    componentDidUpdate(prevProps) {
        if (prevProps.hoverModel !== this.props.hoverModel) {
            this.renderHoverLine(this.props.hoverModel);
        }
        if (prevProps.selectedModel !== this.props.selectedModel) {
            this.renderSelectedLine(this.props.selectedModel);
        }
    }

    componentWillUnmount() {
        $(this.epFigure.current).empty();
    }

    render() {
        return <div ref={this.epFigure} />;
    }
}

OutputFigure.propTypes = {
    endpoint: PropTypes.object.isRequired,
    hoverModel: PropTypes.object,
    selectedModel: PropTypes.object,
};

export default OutputFigure;
