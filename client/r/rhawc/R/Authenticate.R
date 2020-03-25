#' r hawc client functions
#'
#' This function authenticates a user session. It generates a authorization token
#' from the user's username and password and then saves the root_url and auth_header to global environment.
#' Auth_header is the header containing the authorization token.
#'
#' @param username User's username address for accound associated with \code{root_url}
#' @param password User's password
#'
#' @examples
#' \dontrun{authenticate("email@email.com", getPass(), "https://hawcprd.epa.gov")}
#'
#' @import getPass
#' @import httr
#' @import plyr
#' @export
authentication <- function(username, password, root_url) {
  response = POST(paste0(root_url, "/user/api/token-auth/"),
                  body = list(username = username, password = password), encode = "json")
  token = (content(response))[[1]]

  # Set root_url and auth_header as global env variables (seems bad form, find different solution)
  root_url <<- root_url
  auth_header <<- httr::add_headers(Authorization=paste('Token',
                                                        token,sep=' '),
                                    'Content-Type'="application/json")
}

#' @export
get_ <- function(url, header = auth_header) {
  response = GET(url, header)
  if (response$status_code >= 400 & response$status_code < 500) {
    stop("An exception occured in the HAWC client module") }

  else if (response$status_code == 500) {
    stop("An exception occured on the HAWC server") }

  else {
    #response.list = content(response)
    #response.list = lapply(response.list, lapply, function(x)ifelse(is.null(x), NA, x))
    #response.df = rbind.fill(lapply(response.list, as.data.frame))
    #return(response.df)
    print("worked")
  }
}

#' @export
post_ <- function(url, header = auth_header, ...) {
  response = POST(url, header, ...)
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

#' @export
lit_import_hero <- function(assessment_id, title, description, ids) {
  url = paste0(root_url, "/lit/api/search/")
  pc_json <- list(assessment = assessment_id,
                  search_type = "i",
                  source = 2,
                  title = title,
                  description = description,
                  search_string = paste(unlist(ids), collapse=','))

  response = POST(url, auth_header, body = pc_json, encode = "json", verbose())
  response.list = content(response)
  response.df = as.data.frame(response.list)
  return(response.df)
  ###not working
}

#' @export
lit_tags <- function(assessment_id) {
  url = paste0(root_url, "/lit/api/assessment/", assessment_id, "/tags/")
  response = get_(url)
  return(response)
}

#' @export
lit_reference_tags <- function(assessment_id) {
  url = paste0(root_url, "/lit/api/assessment/", assessment_id, "/reference-tags/")
  response = get_(url)
  return(response)
}

#' @export
lit_import_reference_tags <- function(assessment_id, csv, operation = "append") {
  csv.string <- readr::format_csv(csv, col_names = TRUE)
  url = paste0(root_url, "/lit/api/assessment/", assessment_id, "/reference-tags/")
  response = post_(url,
                   auth_header,
                   body = list(csv = csv.string,
                               operation = operation),
                   encode = "json",
                   verbose())
  return(response)
}

#' @export
lit_reference_ids <- function(assessment_id) {
  url = paste0(root_url, "/lit/api/assessment/", assessment_id, "/reference-ids/")
  response = get_(url)
  return(response)
}

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

#' @export
rob_data <- function(assessment_id) {
  url = paste0(root_url, "/rob/api/assessment/", assessment_id, "/export/")
  response = get_(url)
  return(response)
}

#' @export
rob_full_data <- function(assessment_id) {
  url = paste0(root_url, "/rob/api/assessment/", assessment_id, "/full-export/")
  response = get_(url)
  return(response)
}

#' @export
ani_data <- function(assessment_id) {
  url = paste0(root_url, "/ani/api/assessment/", assessment_id, "/full-export/")
  response = get_(url)
  return(response)
}

#' @export
ani_data_summary <- function(assessment_id) {
  url = paste0(root_url, "/ani/api/assessment/", assessment_id, "/endpoint-export/")
  response = get_(url)
  return(response)
}

#' @export
epi_data <- function(assessment_id) {
  url = paste0(root_url, "/epi/api/assessment/", assessment_id, "/export/")
  response = get_(url)
  return(response)
}

#' @export
epimeta_data <- function(assessment_id) {
  url = paste0(root_url, "/epi-meta/api/assessment/", assessment_id, "/export/")
  response = get_(url)
  return(response)
}

#' @export
invitro_data <- function(assessment_id) {
  url = paste0(root_url, "/in-vitro/api/assessment/", assessment_id, "/full-export/")
  response = get_(url)
  return(response)
}

#' @export
visual_list <- function(assessment_id) {
  url = paste0(root_url, "/summary/api/visual/?assessment_id=", assessment_id)
  response = get_(url)
  return(response)
}










