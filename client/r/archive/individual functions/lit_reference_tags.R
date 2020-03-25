#' lit_reference_tags
#'
#' Get request for lit_reference_tags
#'
#' @param assessment_id HAWC assessment id, provided as an integer
#' @return Dataframe with variables reference_id and tag_id
#' @import httr
#' @export
lit_reference_tags <- function(assessment_id) {
  url = paste0(root_url, "/lit/api/assessment/", assessment_id, "/reference-tags/")
  response = get_(url)
  return(response)
}
