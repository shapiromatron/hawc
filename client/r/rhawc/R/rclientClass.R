#' r client functions
#'
#' pretty please work
#'
#' @import httr
#' @import plyr
#' @export
HawcClient <- function(baseUrl){

  # local environment variables
  thisEnv <- environment()

  # persistent "state"
  root_url <- baseUrl
  #   token <- ""

  checkIsAuthenticated <- function(){
    if((nchar(get("token", thisEnv))==0)){
      stop('Authentication required')
    }
    else if (get("token", thisEnv) == 'Unable to log in with provided credentials.') {
      stop('Unable to log in with provided credentials.')
    }
  }
  get_ = function(url) {
    response = GET(url, add_headers(Authorization=paste('Token', get("token", thisEnv),sep=' '),
                                    'Content-Type'="application/json"))
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
  post_ = function(url, ...) {
    response = POST(url, add_headers(Authorization=paste('Token', get("token", thisEnv),sep=' '),
                                     'Content-Type'="application/json"), ...)
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
  # the methods which will be exposed by the client
  me <- list(
    authenticate = function(username, password){
      response = POST(paste0(root_url, "/user/api/token-auth/"),
                      body = list(username = username, password = password), encode = "json")
      token = (content(response))[[1]]
      assign("token", token, thisEnv)
    },
    doSomethingAuthenticated = function(){
      checkIsAuthenticated()
      return(TRUE)
    },
    lit_import_hero = function(assessment_id, title, description, ids) {
      url = paste0(root_url, "/lit/api/search/")
      pc_json <- list(assessment = assessment_id,
                      search_type = "i",
                      source = 2,
                      title = title,
                      description = description,
                      search_string = paste(unlist(ids), collapse=','))

      response = POST(url,
                      add_headers(Authorization=paste('Token', get("token", thisEnv),sep=' '),
                                  'Content-Type'="application/json"),
                      body = pc_json,
                      encode = "json")
      response.list = content(response)
      response.df = as.data.frame(response.list)
      return(response.df)
    },
    lit_tags = function(assessment_id) {
      url = paste0(root_url, "/lit/api/assessment/", assessment_id, "/tags/")
      response = get_(url)
      return(response)
    },
    lit_reference_tags = function(assessment_id) {
      url = paste0(root_url, "/lit/api/assessment/", assessment_id, "/reference-tags/")
      response = get_(url)
      return(response)
    },
    lit_import_reference_tags = function(assessment_id, csv, operation = "append") {
      csv.string <- readr::format_csv(csv, col_names = TRUE)
      url = paste0(root_url, "/lit/api/assessment/", assessment_id, "/reference-tags/")
      response = post_(url,
                       body = list(csv = csv.string,
                                   operation = operation),
                       encode = "json")
      return(response)
    },
    lit_reference_ids = function(assessment_id) {
      url = paste0(root_url, "/lit/api/assessment/", assessment_id, "/reference-ids/")
      response = get_(url)
      return(response)
    },
    lit_references = function(assessment_id) {
      url = paste0(root_url, "/lit/api/assessment/", assessment_id, "/references-download/")
      response = get_(url)
      return(response)
    },
    rob_data = function(assessment_id) {
      url = paste0(root_url, "/rob/api/assessment/", assessment_id, "/export/")
      response = get_(url)
      return(response)
    },
    rob_full_data = function(assessment_id) {
      url = paste0(root_url, "/rob/api/assessment/", assessment_id, "/full-export/")
      response = get_(url)
      return(response)
    },
    ani_data = function(assessment_id) {
      url = paste0(root_url, "/ani/api/assessment/", assessment_id, "/full-export/")
      response = get_(url)
      return(response)
    },
    ani_data_summary = function(assessment_id) {
      url = paste0(root_url, "/ani/api/assessment/", assessment_id, "/endpoint-export/")
      response = get_(url)
      return(response)
    },
    epi_data = function(assessment_id) {
      url = paste0(root_url, "/epi/api/assessment/", assessment_id, "/export/")
      response = get_(url)
      return(response)
    },
    epimeta_data = function(assessment_id) {
      url = paste0(root_url, "/epi-meta/api/assessment/", assessment_id, "/export/")
      response = get_(url)
      return(response)
    },
    invitro_data = function(assessment_id) {
      url = paste0(root_url, "/in-vitro/api/assessment/", assessment_id, "/full-export/")
      response = get_(url)
      return(response)
    },
    visual_list = function(assessment_id) {
      url = paste0(root_url, "/summary/api/visual/?assessment_id=", assessment_id)
      response = get_(url)
      return(response)
    }
  )

  # magic to package things up and return what we want
  assign('this', me, envir=thisEnv)
  class(me) <- append(class(me), "HawcClient")
  return(me)
}
