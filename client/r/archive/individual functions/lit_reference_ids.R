#' lit_reference_ids
#'
#' Get request for lit reference ids
#'
#' @param assessment_id HAWC assessment id, provided as an integer
#' @return Dataframe with variables reference_id, hero_id, pubmed_id
#' @import httr
#' @export
lit_reference_ids <- function(assessment_id) {
  url = paste0(root_url, "/lit/api/assessment/", assessment_id, "/reference-ids/")
  response = get_(url)
  return(response)
}
