#' ani_data
#'
#' Get resquest for animal data
#'
#' @param assessment_id HAWC assessment, provided as an integer
#' @return Dataframe
#' @import httr
#' @export
ani_data <- function(assessment_id) {
  url = paste0(root_url, "/ani/api/assessment/", assessment_id, "/full-export/")
  response = get_(url)
  return(response)
}
