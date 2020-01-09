from typing import NamedTuple


class FlavoredText(NamedTuple):
    prime: str
    epa: str


text_mapping = dict(
    ani__endpoint_form__effects=FlavoredText(
        prime="Any additional descriptive-tags used to categorize the outcome",
        epa="For now, use the endpoint specific overall study evaluation rating of \"high\", \"medium\", \"low\", or \"uninformative\""
    ),
    ani__endpoint_form__name=FlavoredText(
        prime="""
            Short-text used to describe the endpoint.
            Should include observation-time,
            if multiple endpoints have the same observation time.""",
        epa="""
            Short-text used to describe the endpoint/adverse
            outcome. As a first pass during extraction, use
            the endpoint name as presented in the study. Do
            not add units &mdash; units are summarized in a separate
            extraction field. Once extraction is complete for
            an assessment, endpoint/adverse outcomes names may
            be adjusted to use terms that best work across
            studies or assessments using the data clean-up tool
            (the original name as presented in the study will
            be retained in the "Endpoint Name in Study" field). If the
            endpoint is a repeated measure, then indicate the
            time in parentheses, e.g., running wheel activity
            (6 wk), using the abbreviated format: seconds = sec,
            minutes = min, hours = h, days = d, weeks = wk,
            months = mon, years = y.
            """
    ),
    ani__endpoint_form__create=FlavoredText(
        prime="""
            Create a new endpoint. An endpoint may should describe one
            measure-of-effect which was measured in the study. It may
            or may not contain quantitative data.
        """,
        epa="""
            Create a new endpoint. An endpoint should describe
            one measure-of-effect which was measured in the study.
            It may or may not contain quantitative data. For
            endpoint terminology, use the reference document
            "<a href="https://hawcprd.epa.gov/assessment/100000039/">Recommended
            Terminology for Outcomes/Endpoints</a>."
        """,
    ),
    riskofbias__riskofbiasassessment_help_text_default=FlavoredText(
        prime=(
            "<p>When a study is entered into the HAWC database for use in an assessment, "
            "risk of bias metrics can be entered for a metric of bias for each study. "
            "Risk of Bias metrics are organized by domain. The following questions are "
            "required for evaluation for this assessment.</p>"
        ),
        epa="""<p>Study evaluations are performed on an endpoint/outcome-specific basis.
                For each evaluation domain, core and prompting questions are provided to
                guide the reviewer in assessing different aspects of study design and
                conduct related to reporting, risk of bias and study sensitivity.
                For some domains (see below), additional outcome- or chemical-specific
                refinements to the criteria used to answer the questions should be developed
                <em>a priori</em> by reviewers. Each domain receives a judgment of
                <em>Good</em>, <em>Adequate</em>, <em>Deficient</em>, <em>Not Reported</em>
                or <em>Critically Deficient</em> accompanied by the rationale and primary
                study-specific information supporting the judgment.&nbsp;Once all domains
                are evaluated, a confidence rating of <em>High</em>, <em>Medium</em>, or
                <em>Low</em> confidence or <em>Uninformative</em> is assigned for each
                endpoint/outcome from the study.&nbsp;The overall confidence rating
                should, to the extent possible, reflect interpretations of the potential
                influence on the results (including the direction and/or magnitude of
                influence) across all domains.&nbsp;The rationale supporting the overall
                confidence rating should be documented clearly and consistently, including
                a brief description of any important strengths and/or limitations that were
                identified and their potential impact on the overall confidence.</p>
                <p>Note that due to current limitations in HAWC, domain judgments and overall
                ratings for all individual endpoints/outcomes assessed in a study will need
                to be entered using a single drop-down selection and free-text box for each
                study. Thus, all the reviewer decisions (and the supporting rationale) drawn
                at the level of a specific cohort or individual endpoint within a study must
                be described within a single free-text box.&nbsp;Within the text boxes, please
                remember to call out each of the specific judgments and rationales. A good
                form to follow for the text boxes is '<strong><em>Endpoint/Outcome – Judgment
                – Rationale</em></strong>'. When selecting the representative rating for the
                domains and overall rating (i.e., the drop-down selection with the associated
                color code), it is typically most appropriate to select the judgment that
                best represents an average of the responses for the endpoint/outcome evaluated
                in that study, considering the pre-defined importance of individual
                outcomes/health effects to the assessment (see Overall Confidence examples).</p>
                <p>Follow <a href='https://hawcprd.epa.gov/assessment/100000039/' target='_blank'><strong>link</strong></a>
                to see attachments that contain example answers to the animal study evaluation domains.
                <em>It is really helpful to have this document open when conducting reviews.</em></p>
                <p>Follow <a href='https://hawcprd.epa.gov/assessment/100000039/' target='_blank'><strong>link</strong></a>
                to see attachments that contain example prompting and follow-up questions for epidemiological studies.</p>
            """,
    )
)
