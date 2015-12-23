import React, { Component, PropTypes } from 'react';
import { Provider } from 'react-redux';
import { ReduxRouter } from 'redux-router';
import DevTools from './DevTools';

class Counter extends Component {
    constructor(props) {
        super(props);
        this.state = { counter: 0 };
        this.interval = setInterval(() => this.tick(), 1000);
    }

    tick() {
        this.setState({
            counter: this.state.counter + this.props.increment
        });
    }

    componentWillUnmount() {
        clearInterval(this.interval);
    }

    render() {
        return (
            <h1 style={{ color: this.props.color }}>
                Counter ({this.props.increment}): {this.state.counter}
            </h1>
        );
    }
}

export default class App extends Component {
    render() {
        const { store } = this.props
        return (
            <Provider store={store}>
                <div>
                    <ReduxRouter/>
                    <DevTools/>
                    <Counter increment={1} color={NICE} />
                    <Counter increment={3} color={SUPER_NICE} />
                </div>
            </Provider>
        );
    }
}

App.propTypes = {
    store: PropTypes.object.isRequired
}
