#' lit_import_hero
#'
#' Post request to attach hero tags to an assessment (maybe?)
#'
#' @param assessment_id HAWC assessment id, provided as an integer
#' @param title title
#' @param description title
#' @param ids List of hero id's to tag to assessmnet (maybe?)
#' @return Named list
#' @import httr
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
}
