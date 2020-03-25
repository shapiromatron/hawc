#' epimeta_data
#'
#' Get request for meta epidemiologic data
#'
#' @param assessment_id HAWC assessment id, provided as an integer
#' @return Dataframe
#' @import httr
#' @export
epimeta_data <- function(assessment_id) {
  url = paste0(root_url, "/epi-meta/api/assessment/", assessment_id, "/export/")
  response = get_(url)
  return(response)
}
