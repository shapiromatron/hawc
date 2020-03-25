#' ani_data_summary
#'
#' Get request for summary animal data
#'
#' @param assessment_id HAWC assessment id, provided as an integer
#' @return Dataframe
#' @import httr
#' @export
ani_data_summary <- function(assessment_id) {
  url = paste0(root_url, "/ani/api/assessment/", assessment_id, "/endpoint-export/")
  response = get_(url)
  return(response)
}
