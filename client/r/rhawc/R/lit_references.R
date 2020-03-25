#' lit_references
#'
#' Get request for lit references
#'
#' @param assessment_id HAWC assessment id, provided as an integer
#' @return Dataframe with a LOT of reference information
#' @import httr
#' @export
lit_references <- function(assessment_id) {
  url = paste0(root_url, "/lit/api/assessment/", assessment_id, "/references-download/")
  response = get_(url)
  return(response)
}
