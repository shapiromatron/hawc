// adapted from `https://observablehq.com/@d3/word-cloud`
import * as d3 from "d3";
import cloud from "d3-cloud";
import {observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import ReactDOM from "react-dom";
import {createRoot} from "react-dom/client";
import Loading from "shared/components/Loading";
import VisualToolbar from "shared/components/VisualToolbar";

import $ from "$";

const padding = 0,
    MIN_REFS = 2,
    stopwords = new Set(
        "i,me,my,myself,we,us,our,ours,ourselves,you,your,yours,yourself,yourselves,he,him,his,himself,she,her,hers,herself,it,its,itself,they,them,their,theirs,themselves,what,which,who,whom,whose,this,that,these,those,am,is,are,was,were,be,been,being,have,has,had,having,do,does,did,doing,will,would,should,can,could,ought,i'm,you're,he's,she's,it's,we're,they're,i've,you've,we've,they've,i'd,you'd,he'd,she'd,we'd,they'd,i'll,you'll,he'll,she'll,we'll,they'll,isn't,aren't,wasn't,weren't,hasn't,haven't,hadn't,doesn't,don't,didn't,won't,wouldn't,shan't,shouldn't,can't,cannot,couldn't,mustn't,let's,that's,who's,what's,here's,there's,when's,where's,why's,how's,a,an,the,and,but,if,or,because,as,until,while,of,at,by,for,with,about,against,between,into,through,during,before,after,above,below,to,from,up,upon,down,in,out,on,off,over,under,again,further,then,once,here,there,when,where,why,how,all,any,both,each,few,more,most,other,some,such,no,nor,not,only,own,same,so,than,too,very,say,says,said,shall".split(
            ","
        )
    ),
    getWords = text => {
        const words = text
            .split(/[\s.]+/g)
            .map(w => w.replace(/^[“‘"\-—()[\]{},]+/g, ""))
            .map(w => w.replace(/[;:.!?()[\]{},"'’”\-—]+$/g, ""))
            .map(w => w.replace(/['’]s$/g, ""))
            .map(w => w.substring(0, 30))
            .map(w => w.toLowerCase())
            .filter(w => w && w.length > 2 && !stopwords.has(w));

        const data = d3
                .rollups(
                    words,
                    group => group.length,
                    w => w
                )
                .sort(([, a], [, b]) => d3.descending(a, b))
                .slice(0, 100) // top N words
                .map(([text, value]) => ({text, value})),
            fontScale = d3
                .scaleLinear()
                .domain(d3.extent(data, d => d.value))
                .range([300, 900]),
            colorScale = d3
                .scaleSqrt()
                .domain(d3.extent(data, d => d.value))
                .range([0.4, 1]);

        return data.map(d => {
            return {
                text: d.text,
                value: fontScale(d.value),
                fillColor: d3.interpolateGreys(colorScale(d.value)),
            };
        });
    },
    plot = (el, text) => {
        const data = getWords(text),
            width = $(el).width(),
            height = Math.ceil(width * 0.4),
            toolbarNode = $("<div>");

        const svg = d3
            .create("svg")
            .attr("role", "image")
            .attr("aria-label", "A wordcloud of frequent words in the selected literature")
            .attr("viewBox", [0, 0, width, height])
            .attr("font-family", "sans-serif")
            .attr("text-anchor", "middle");

        cloud()
            .size([width, height])
            .words(data.map(d => Object.create(d)))
            .padding(padding)
            .font("sans-serif")
            .rotate(0)
            .on("word", ({size, x, y, rotate, text, fillColor}) => {
                svg.append("text")
                    .attr("font-size", size)
                    .style("fill", fillColor)
                    .attr("transform", `translate(${x},${y}) rotate(${rotate})`)
                    .text(text)
                    .on("mouseenter", function () {
                        d3.select(this)
                            .transition()
                            .duration(120)
                            .style("fill", "#87ceff")
                            .attr("font-size", size * 1.1);
                    })
                    .on("mouseleave", function () {
                        d3.select(this)
                            .transition()
                            .duration(60)
                            .style("fill", fillColor)
                            .attr("font-size", size);
                    });
            })
            .start();

        $(el).empty().append(svg.node()).append(toolbarNode);

        const root = createRoot(1);
        root.render(<VisualToolbar svg={svg.node()} />, toolbarNode.get(0));
    };

@observer
class Wordcloud extends Component {
    constructor(props) {
        super(props);
        this.svgDiv = React.createRef();
        this.updatePlot = this.updatePlot.bind(this);
    }
    updatePlot() {
        const text = this.props.references.map(ref => ref.data.title).join(" ");
        if (this.svgDiv.current) {
            plot(this.svgDiv.current, text);
        }
    }
    componentDidMount() {
        setTimeout(this.updatePlot, 1);
    }
    componentDidUpdate() {
        setTimeout(this.updatePlot);
    }
    render() {
        const {references} = this.props;

        if (references.length < MIN_REFS) {
            return (
                <p className="text-muted">A wordcloud requires at least {MIN_REFS} references.</p>
            );
        }

        return (
            <div ref={this.svgDiv} className="clearfix pb-2" style={{"text:hover": "red"}}>
                <Loading />
            </div>
        );
    }
}
Wordcloud.propTypes = {
    references: PropTypes.array,
    onFilter: PropTypes.func,
};

export default Wordcloud;
