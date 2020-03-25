#' visual_list
#'
#' Get request for in visual list (?)
#'
#' @param assessment_id HAWC assessment id, provided as an integer
#' @return Dataframe orrrr a list?
#' @import httr
#' @export
visual_list <- function(assessment_id) {
  url = paste0(root_url, "/summary/api/visual/?assessment_id=", assessment_id)
  response = get_(url)
  return(response)
}
