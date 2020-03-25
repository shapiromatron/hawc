#' lit_tags
#'
#' Get request for lit tags
#'
#' @param assessment_id HAWC assessment id, provided as an integer
#' @return Dataframe with variables id, depth, name, nested_name
#' @import httr
#' @export
lit_tags <- function(assessment_id) {
  url = paste0(root_url, "/lit/api/assessment/", assessment_id, "/tags/")
  response = get_(url)
  return(response)
}
