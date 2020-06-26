class AssessmentCacheKeys:
    def endpoint_doses_heatmap(assessment_id: int, unpublished: bool):
        return (
            f"assessment-{assessment_id}-bioassay-endpoint-doses-heatmap-unpublished-{unpublished}"
        )

