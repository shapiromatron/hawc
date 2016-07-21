import React from 'react';

import {
    BMDLine,
} from 'bmd/models/model';


class OutputFigure extends React.Component {

    componentDidMount(){
        let {endpoint} = this.props;
        this.plt = endpoint.renderPlot($(this.refs.epFigure)).plot;
        this.renderSelectedLine(this.props.selectedModel);
    }

    renderHoverLine(model){
        if (model === null){
            if (this.hover_line){
                this.hover_line.destroy();
                delete this.hover_line;
            }
        } else {

            if (this.selected_line && model.id == this.selected_line.model.id){
                return;
            }

            this.hover_line = new BMDLine(model, this.plt);
            this.hover_line.render();
        }
    }

    renderSelectedLine(model){
        if (model === null || (this.selected_line && this.selected_line.model.id !== model.id)){
            if (this.selected_line){
                this.selected_line.destroy();
                delete this.selected_line;
            }
        }

        if (model !== null){
            this.selected_line = new BMDLine(model, this.plt);
            this.selected_line.render();
        }
    }

    componentWillReceiveProps(nextProps){
        if (nextProps.hoverModel !== this.props.hoverModel){
            this.renderHoverLine(nextProps.hoverModel);
        }
        if (nextProps.selectedModel !== this.props.selectedModel){
            this.renderSelectedLine(nextProps.selectedModel);
        }
    }

    componentWillUnmount(){
        $(this.refs.epFigure).empty();
    }

    render() {
        return (
            <div className="span4"
                 style={{height: '300px', width: '300px'}}
                 ref='epFigure'>
            </div>
        );
    }
}

OutputFigure.propTypes = {
    endpoint: React.PropTypes.object.isRequired,
    hoverModel: React.PropTypes.object,
    selectedModel: React.PropTypes.object,
};

export default OutputFigure;
