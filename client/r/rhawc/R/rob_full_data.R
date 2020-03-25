#' rob_full_data
#'
#' Get request for full risk of bias data
#'
#' @param assessment_id HAWC assessment id, provided as an integer
#' @return Dataframe
#' @import httr
#' @export
rob_full_data <- function(assessment_id) {
  url = paste0(root_url, "/rob/api/assessment/", assessment_id, "/full-export/")
  response = get_(url)
  return(response)
}
