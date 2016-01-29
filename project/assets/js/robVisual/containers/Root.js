import React, { Component, PropTypes } from 'react';


class EffectSelector extends Component {
    render(){
        return (
            <div>
                <select multiple="true"></select>
                <p className='help-block'>
                    After effects have loaded, render options here.
                </p>
            </div>
        );
    }
}

class ScoreSlider extends Component {
    render(){
        return (
            <div>
                <input type='range' min='0' max='100'></input>
                <p className='help-block'>
                    After study-quality values have loaded, render options here.
                </p>
            </div>
        );
    }
}

class ApplyFilters extends Component {
    render(){
        return (
            <div>
                <button type='button' className='btn btn-primary'>Apply filters</button>
                <p className='help-block'>
                    Can't really be live, but if they press this button it refilters.
                    It should select all the endpoint values as an array in the state,
                    and then pass them using the `effect` parameter in the ajax call.
                    Then, based on the study-quality value on the slider, get a list
                    of study_ids and put in the `study_id`. Should then return a list
                    of enpdoints, or throw an error if the values are too large.
                </p>
                <strong>Example possible valid call:</strong>
                <ul>
                    <li><a href='/ani/api/endpoint/rob_filter/?assessment_id=126&effect[]=other'>By effect</a></li>
                    <li><a href='/ani/api/endpoint/rob_filter/?assessment_id=126&study_id[]=52469&study_id[]=52471'>By study ids</a></li>
                </ul>
            </div>
        );
    }
}


class EndpointCard extends Component {
    render(){
        return (
            <div className='span3'>
                <h4>Endpoint name<br/>(with link to endpoint)</h4>
                <p>Dose-response plot placeholder</p>
                <p>Extra content text here...</p>
                <button type='button' className='btn btn-default'>Show detail modal</button>
            </div>
        );
    }
}


class EndpointCardContainer extends Component {

    renderEndpointCard(d,i){
        return <EndpointCard key={i} />;
    }

    render(){
        let eps = [1,2,3,1,2,3,1,2,3];
        return (
            <div className='row-fluid'>
                {eps.map(this.renderEndpointCard.bind(this))}
            </div>
        );
    }
}


export default class Root extends Component {

    render() {
        return (
            <div>
                <h1>Risk of bias filtering</h1>
                <EffectSelector />
                <ScoreSlider />
                <ApplyFilters />
                <EndpointCardContainer/>
            </div>
        );
    }
}

Root.propTypes = {
    store: PropTypes.object.isRequired,
};
