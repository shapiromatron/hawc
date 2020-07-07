import React, {Component} from "react";
import PropTypes from "prop-types";
import {connect} from "react-redux";

class Header extends Component {
    renderHelpText(hawc_flavor, assessment_id) {
        if (hawc_flavor !== "EPA") {
            return null;
        } else if (assessment_id == "100500031") {
            // TODO - remove 100500031 hack
            return (
                <p>
                    Please disregard the drop-down selections. They will be assigned as
                    &quot;Not-applicable&quot; post-review.
                </p>
            );
        } else {
            // TODO - make this a hawc-flavor setting via a lookup table instead of logic
            return (
                <div>
                    <p>
                        Study evaluations are performed on an endpoint/outcome-specific
                        basis.&nbsp;&nbsp;For each evaluation domain, core and prompting questions
                        are provided to guide the reviewer in assessing different aspects of study
                        design and conduct related to reporting, risk of bias and study
                        sensitivity.&nbsp;For some domains (see below), additional outcome- or
                        chemical-specific refinements to the criteria used to answer the questions
                        should be developed <em>a priori</em> by reviewers.&nbsp;Each domain
                        receives a judgment of <em>Good</em>, <em>Adequate</em>, <em>Deficient</em>,{" "}
                        <em>Not Reported</em> or <em>Critically Deficient</em> accompanied by the
                        rationale and primary study-specific information supporting the
                        judgment.&nbsp;Once all domains are evaluated, a confidence rating of{" "}
                        <em>High</em>, <em>Medium</em>, or <em>Low</em> confidence or{" "}
                        <em>Uninformative</em> is assigned for each endpoint/outcome from the
                        study.&nbsp;The overall confidence rating should, to the extent possible,
                        reflect interpretations of the potential influence on the results (including
                        the direction and/or magnitude of influence) across all domains.&nbsp;The
                        rationale supporting the overall confidence rating should be documented
                        clearly and consistently, including a brief description of any important
                        strengths and/or limitations that were identified and their potential impact
                        on the overall confidence.
                    </p>
                    <p>
                        Note that due to current limitations in HAWC, domain judgments and overall
                        ratings for all individual endpoints/outcomes assessed in a study will need
                        to be entered using a single drop-down selection and free-text box for each
                        study. Thus, all the reviewer decisions (and the supporting rationale) drawn
                        at the level of a specific cohort or individual endpoint within a study must
                        be described within a single free-text box.&nbsp;Within the text boxes,
                        please remember to call out each of the specific judgments and
                        rationales.&nbsp;A good form to follow for the text boxes is ‘
                        <strong>
                            <em>Endpoint/Outcome – Judgment – Rationale</em>
                        </strong>
                        ’.&nbsp;When selecting the representative rating for the domains and overall
                        rating (i.e., the drop-down selection with the associated color code), it is
                        typically most appropriate to select the judgment that best represents an
                        average of the responses for the endpoint/outcome evaluated in that study,
                        considering the pre-defined importance of individual outcomes/health effects
                        to the assessment (see Overall Confidence examples).
                    </p>
                    <p>
                        Follow<strong> </strong>
                        <a href="/assessment/100000039/" target="_blank">
                            <strong>link</strong>
                        </a>{" "}
                        to see attachments that contain example answers to the animal study
                        evaluation domains.{" "}
                        <em>
                            It is really helpful to have this document open when conducting reviews.{" "}
                        </em>
                    </p>
                    <p>
                        Follow<strong>&nbsp;</strong>
                        <a href="/assessment/100000039/" target="_blank">
                            <strong>link</strong>
                        </a>
                        <strong>&nbsp;</strong>to see attachments that contain example prompting and
                        follow-up questions for epidemiological studies.
                    </p>
                </div>
            );
        }
    }

    render() {
        let headerText,
            {isForm, display, assessment_id, hawc_flavor} = this.props.config;
        if (isForm) {
            headerText = display == "final" ? "Final review" : "Review";
        } else if (display == "all") {
            headerText = "Show all active reviews";
        }

        return (
            <div>
                <h3>{headerText}</h3>
                {this.renderHelpText(hawc_flavor, assessment_id)}
            </div>
        );
    }
}

function mapStateToProps(state) {
    return {
        config: state.config,
    };
}

Header.propTypes = {
    config: PropTypes.shape({
        isForm: PropTypes.object,
        display: PropTypes.object,
        assessment_id: PropTypes.object,
        hawc_flavor: PropTypes.object,
    }),
};

export default connect(mapStateToProps)(Header);
