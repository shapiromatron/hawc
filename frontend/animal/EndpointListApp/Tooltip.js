import PropTypes from "prop-types";
import React, {Component} from "react";

class Tooltip extends Component {
    render() {
        const {d} = this.props;
        const classification = [d.system, d.organ, d.effect, d.effect_subtype]
            .filter(el => el != null && el !== "")
            .join("<br/>");
        return (
            <div style={{width: 300}}>
                <table className="table table-sm table-striped">
                    <colgroup>
                        <col width={"100px"} />
                        <col width={"200px"} />
                    </colgroup>
                    <tbody>
                        <tr>
                            <th>Study</th>
                            <td>{d["study citation"]}</td>
                        </tr>
                        <tr>
                            <th>Animal Group</th>
                            <td>{d["animal group name"]}</td>
                        </tr>
                        <tr>
                            <th>
                                System,
                                <br />
                                organ,
                                <br />
                                effect, etc.
                            </th>
                            <td dangerouslySetInnerHTML={{__html: classification}}></td>
                        </tr>
                        <tr>
                            <th>Endpoint</th>
                            <td>{d["endpoint name"]}</td>
                        </tr>
                        <tr>
                            <th>{d.type.toUpperCase()}</th>
                            <td>
                                {d.dose} {d["dose units name"]}
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        );
    }
}
Tooltip.propTypes = {
    d: PropTypes.object.isRequired,
};

export default Tooltip;
