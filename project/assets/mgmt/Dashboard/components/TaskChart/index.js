import React, { PureComponent, PropTypes } from 'react';
import vg from 'vega';
import _ from 'underscore';

import './TaskChart.css';


class TaskChart extends PureComponent {

    constructor(props) {
        super(props);
        this.state = {
            vis: null,
        };
    }

    componentDidMount() {
        const data = this.formatData(),
            spec = this._spec();

        vg.parse.spec(spec, (chart) => {
            const vis = chart({ el: this.graphMount });
            vis.data('tasks').insert(data);
            vis.update();
            this.setState({ vis });
        });
    }

    componentDidUpdate(prevProps, prevState) {
        const { vis } = this.state,
            data = this.formatData();

        console.log('data', data);
        if (vis) {
            vis.data('tasks').remove(() => true).insert(data);
            vis.update();
        }
    }

    formatData() {
        let { tasks } = this.props,
            // reshape tasks to only have current status and status date, group by current status, then transform tasks into { date: count} objects
            // data => [{completed: [{'2016-11-15T17:51:23.463608Z': 1, '2016-11-18T17:31:23.4223Z': 2}]}, 'not started': [{'2016-09-26T17:17:53.404134Z': 1}]]
            counts = { 'not_started': tasks.length, started: 1, completed: 1, abandoned: 1},
            data = _.chain(tasks)
                    .filter((task) => task.status_display != 'not started' )
                    .map((task) =>  {
                        let date = task.status_display == 'abandoned' ? task.completed : task[task.status_display];
                        return {
                            started: Date.parse(task.started || date),
                            status: task.status,
                            status_display: task.status_display,
                            date: Date.parse(date),
                        }})
                    .sort((a, b) => a.started - b.started)
                    .map((task, i) => {
                        return [{ status_rank: 10, status_display: 'not started', x: task.started, y: counts['not_started']-- }, { status_rank: task.status, status_display: task.status_display, x: task.date, y: counts[task.status_display]++ }]
                    })
                    .flatten()
                    .value()
        return data;
    }

    render() {
        return <div ref={(e) => this.graphMount = e} />
    }

    _spec() {
        const { width, height, padding } = this.props.chartData;
        return {
            width,
            height: 800,
            padding,
            data: [
                {
                    name: 'tasks',
                    format: {
                        type: 'json',
                        parse: { x: 'date', status_rank: 'number', y: 'number', status_display: 'string'}
                    },
                    transform: [
                        { type: 'sort', by: ['-status_rank'] }
                    ]
                }
            ],
            scales: [
                {
                    name: 'x',
                    type: 'time',
                    domain: { data: 'tasks', field: 'x' },
                    range: 'width'
                }, {
                    name: 'y',
                    type: 'linear',
                    domain: { data: 'tasks', field: 'y'},
                    range: 'height',
                    nice: true,
                    sort: {
                        field: 'date'
                    }
                }, {
                    name: 'color',
                    type: 'ordinal',
                    domain: { data: 'tasks', field: 'status_rank'},
                    range: ['#CFCFCF', '#FFCC00', '#00CC00', '#CC3333']
                }
            ],
            axes: [
                {
                    type: 'x',
                    scale: 'x',
                    offset: 5,
                    ticks: 5,
                    title: 'Date',
                    layer: 'back',
                    format: '%b %y',
                    formatType: 'time'
                }, {
                    type: 'y',
                    scale: 'y',
                    offset: 5,
                    ticks: 5,
                    title: 'Tasks',
                    layer: 'back'
                }
            ],
            marks: [
                {
                    type: 'group',
                    from: {
                        data: 'tasks',
                        transform: [
                            { type: 'facet', groupby: ['status_rank'] },
                        ]
                    },
                    marks: [
                        {
                            type: 'line',
                            properties: {
                                enter: {
                                    x: { scale: 'x', field: 'x' },
                                    y: { scale: 'y', field: 'y' },
                                    stroke: { scale: 'color', field: 'status_rank' },
                                    strokeWidth: { value: 2 }
                                }
                            }

                        }
                    ]
                }
            ],
            legends:[
                {
                    fill: 'color',
                    offset: -50,
                    properties: {
                        labels: {
                            fontSize: { value: 13 }
                        }
                    },
                    values: ['not started', 'started', 'completed', 'abandoned']
                }
            ]
        }
    }
}

TaskChart.propTypes = {
    tasks: PropTypes.array.isRequired,
    chartData: PropTypes.shape({
        height: PropTypes.number.isRequired,
        width: PropTypes.number.isRequired,
        padding: PropTypes.shape({
            top: PropTypes.number.isRequired,
            right: PropTypes.number.isRequired,
            bottom: PropTypes.number.isRequired,
            left: PropTypes.number.isRequired,
        }).isRequired,
        xTransform: PropTypes.array.isRequired,
        yTransform: PropTypes.array.isRequired
    }).isRequired,
};

export default TaskChart;
