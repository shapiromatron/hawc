#' invitro_data
#'
#' Get request for in vitro data
#'
#' @param assessment_id HAWC assessment id, provided as an integer
#' @return Dataframe
#' @import httr
#' @export
invitro_data <- function(assessment_id) {
  url = paste0(root_url, "/in-vitro/api/assessment/", assessment_id, "/full-export/")
  response = get_(url)
  return(response)
}
