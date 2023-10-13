EPA = dict(
    assessment=dict(
        Assessment=dict(
            enable_project_management=(
                "Enable project management module for data extraction and "
                "study evaluation. If enabled, each study will have multiple "
                "tasks which can be assigned and tracked for completion."
            ),
        ),
    ),
    epi=dict(
        StudyPopulation=dict(
            design=(
                "Choose the most specific description of study design. See “Epidemiology Terms Appendix“ for additional guidance: "
                "<a target='_new' href='https://hawc.epa.gov/assessment/100000039/'>https://hawc.epa.gov/assessment/100000039/</a>. "
                "<span class='important-note'>This field is commonly used in HAWC visualizations</span>"
            ),
        ),
        Outcome=dict(
            name=(
                "Follow “Recommended Terminology for Outcomes/Endpoints“: <a target='_new' href='https://hawc.epa.gov/assessment/100000039/'>https://hawc.epa.gov/assessment/100000039/</a>. "
                "Use title style (capitalize all words). Ex. Hyperthyroidism <span class='important-note'>This field is commonly used in HAWC visualizations</span>"
            ),
            effects=(
                "For now, tag overall study confidence from the Risk of Bias review in this field. Ex. high "
                '<span class="help-text-notes"> To add a new tag, click the "+" button to the right. '
                '</span><span class="help-text-notes">Only create new tags when necessary</span>'
            ),
            system=(
                "Enter biological system affected, following “Recommended Terminology for Outcomes/Endpoints“: "
                "<a target='_new' href='https://hawc.epa.gov/assessment/100000039/'>https://hawc.epa.gov/assessment/100000039/</a>. "
                "Use title style (capitalize all words). Ex. Endocrine"
            ),
            effect=(
                "Enter effect, following “Recommended Terminology for Outcomes/Endpoints“: "
                "<a target='_new' href='https://hawc.epa.gov/assessment/100000039/'>https://hawc.epa.gov/assessment/100000039/</a>. "
                "Use title style (capitalize all words). Ex. Thyroid Hormones "
            ),
            effect_subtype=(
                "Enter effect subtype, following “Recommended Terminology for Outcomes/Endpoints“: "
                "<a target='_new' href='https://hawc.epa.gov/assessment/100000039/'>https://hawc.epa.gov/assessment/100000039/</a>."
                "Use title style (capitalize all words). Ex. Absolute "
                "<i>This field is not mandatory; often no effect subtype is necessary</i>"
            ),
        ),
        Group=dict(
            comparative_name=(
                "For categorical, note if there is a comparison group. Ex. referent; Q2 vs. Q1 "
                + 'The referent group against which exposure or "index" groups are compared is '
                + "typically the group with the lowest or no exposure"
            ),
        ),
    ),
    riskofbias=dict(
        RiskOfBiasAssessment=dict(
            help_text="Detailed instructions for completing study evaluation assessments.",
        ),
    ),
    study=dict(
        Study=dict(
            short_citation="""
                Use this format: last name, year, HERO ID (e.g., Baeder, 1990, 10130). This field
                is used to select studies for visualizations and endpoint filters within HAWC, so
                you may need to add distinguishing features such as chemical name when the
                assessment includes multiple chemicals (e.g., Baeder, 1990, 10130 PFHS). Note:
                Brackets can be added to put the references in LitCiter format in document text,
                e.g., {Baeder, 1990, 10130} or {Baeder, 1990, 10130@@author-year}, but LitCiter
                will not work on HAWC visuals.
                """,
            full_citation=(
                "Complete study citation, in desired format. First author last name, Initial; "
                "Second author last name, Initial; etc. (Year). Title. Journal volume (issue): "
                "pages. Web link"
            ),
            study_identifier="""
                This field may be used in HAWC visualizations when there is a preference not to
                display the HERO ID number, so use author year format, e.g., Smith, 1978, Smith
                and Jones, 1978 or Smith et al., 1978 (for more than 3 authors).
                """,
            ask_author=(
                "Details on correspondence between data-extractor and author (if author contacted). "
                "Please include date and details of the correspondence. The files documenting "
                "the correspondence can also be added to HAWC as attachments and HERO as a "
                "new record, but first it is important to redact confidential or personal "
                "information (e.g., email address)."
            ),
        )
    ),
)
