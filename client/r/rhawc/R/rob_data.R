#' rob_data
#'
#' Get request for risk of bias data
#'
#' @param assessment_id HAWC assessment id, provided as an integer
#' @return Dataframe
#' @import httr
#' @export
rob_data <- function(assessment_id) {
  url = paste0(root_url, "/rob/api/assessment/", assessment_id, "/export/")
  response = get_(url)
  return(response)
}
