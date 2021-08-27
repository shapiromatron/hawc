import React, {Component} from "react";
import PropTypes from "prop-types";
import Plot from "react-plotly.js";

import Loading from "shared/components/Loading";

class PlotFromUrl extends Component {
    static propTypes = {
        url: PropTypes.string,
    };

    constructor(props) {
        super(props);
        this.state = {data: null, error: false};
    }

    componentDidMount() {
        fetch(this.props.url)
            .then(response => response.json())
            .then(json => {
                this.setState({data: json});
            })
            .catch(error => {
                this.setState({error: true});
            });
    }

    render() {
        const {data, error} = this.state;
        if (error) {
            return (
                <p className="text-danger">
                    An error occurred on the server. Please try again later. If the error continues
                    to occur, please let us know!
                </p>
            );
        }
        if (data === null) {
            return <Loading />;
        }
        return (
            <Plot
                data={data.data}
                layout={data.layout}
                useResizeHandler={true}
                style={{width: "100%", height: "100%"}}
            />
        );
    }
}

export default PlotFromUrl;
