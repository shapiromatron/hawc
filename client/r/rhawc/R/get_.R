#' get_
#'
#' Basically GET but prints out error message based on status code or formats request response as a dataframe.
#'
#' @param url Full URL for API request
#' @param header Header for GET request. If \code{NULL} the default is \code{auth_header}, which contains authorization token
#'
#' @import plyr
#' @import httr
#' @export
get_ <- function(url, header = auth_header) {
  response = GET(url, auth_header)
  if (response$status_code >= 400 & response$status_code < 500) {
    stop("An exception occured in the HAWC client module") }

  else if (response$status_code == 500) {
    stop("An exception occured on the HAWC server") }

  else {
    response.list = content(response)
    response.list = lapply(response.list, lapply, function(x)ifelse(is.null(x), NA, x))
    response.df = rbind.fill(lapply(response.list, as.data.frame))
    return(response.df) }
}
