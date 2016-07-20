import React from 'react';

import {
    BMDLine,
} from 'bmd/models/model';


class OutputFigure extends React.Component {

    componentDidMount(){
        let {endpoint} = this.props;
        this.plt = endpoint.renderPlot($(this.refs.epFigure)).plot;
    }

    componentWillReceiveProps(nextProps){
        let hm = nextProps.hoverModel;
        if (hm === null){
            if (this.hover_line){
                this.hover_line.destroy();
                delete this.hover_line;
            }
        } else {
            this.hover_line = new BMDLine(hm, this.plt);
            this.hover_line.render();
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
};

export default OutputFigure;
