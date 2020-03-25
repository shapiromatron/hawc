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
  response = GET(url)
 # if (response$status_code >= 400 & response$status_code < 500) {
#    stop("An exception occured in the HAWC client module") }

 # else if (response$status_code == 500) {
  #  stop("An exception occured on the HAWC server") }

  #else {
  #  response.list = content(response)
  #  response.list = lapply(response.list, lapply, function(x)ifelse(is.null(x), NA, x))
  #  response.df = rbind.fill(lapply(response.list, as.data.frame))
    return(content(response))
}
