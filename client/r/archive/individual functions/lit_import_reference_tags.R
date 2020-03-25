#' lit_import_reference_tags
#'
#' Post request to attach tag_ids to reference_ids from csv file
#'
#' @param assessment_id HAWC assessment id, provided as an integer
#' @param csv Provide csv as data frame (i.e. after using \code{read.csv()})
#' @return Dataframe with variables tag_id and reference_id
#' @import httr
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
