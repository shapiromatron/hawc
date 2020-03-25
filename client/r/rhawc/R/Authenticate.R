#' authenticate
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
#' @export
authenticate <- function(username, password, root_url) {
  response = POST(paste0(root_url, "/user/api/token-auth/"),
                  body = list(username = username, password = password))
  token = (content(response))[[1]]

  # Set root_url and auth_header as global env variables (seems bad form, find different solution)
  root_url <<- root_url
  auth_header <<- httr::add_headers(Authorization=paste('Token',
                                                        token,sep=' '),
                                    'Content-Type'="application/json")
}
