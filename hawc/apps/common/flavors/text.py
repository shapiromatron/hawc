from typing import NamedTuple


class FlavoredText(NamedTuple):
    prime: str
    epa: str


text_mapping = dict(
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
                <p>Domain judgments and overall ratings for all individual endpoints/outcomes
                can be captured by a single (default) response, or you can create override
                responses assigned to individual endpoints, outcomes, or results; provide a
                descriptive label to describe which components the score refers to. Each response
                must have a single default score; when selecting the default representative rating
                for the domains and overall rating (i.e., the drop-down selection with the
                associated color code), it is typically most appropriate to select the judgment
                that best represents the study overall.</p>
                <p>Follow <a href='https://hawcprd.epa.gov/assessment/100000039/' target='_blank'><strong>link</strong></a>
                to see attachments that contain example answers to the animal study evaluation domains.
                <em>It is really helpful to have this document open when conducting reviews.</em></p>
                <p>Follow <a href='https://hawcprd.epa.gov/assessment/100000039/' target='_blank'><strong>link</strong></a>
                to see attachments that contain example prompting and follow-up questions for epidemiological studies.</p>
            """,
    ),
)
