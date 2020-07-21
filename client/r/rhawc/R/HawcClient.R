#" HawcClient
#"
#" This function serves as an R-client to send and receive
#" data from HAWC (Health assessment workspace collaborative)
#"
#" @import getPass
#" @import httr
#" @import plyr
#" @import glue
#" @export
HawcClient = function(baseUrl){

  # constants
  NOT_IMPLEMENTED_ERROR_ = "Not yet implemented; use the Python client until this is available (or contact admins)"
  HAWC_SERVER_ERROR_ = "HAWC server error (contact admins if you think you've found a bug)"

  # local environment variable scope
  thisEnv = environment()

  # persistent state
  root_url = baseUrl
  token = ""

  # private methods
  headers_ = function() {
    headers <- c("Content-Type"="application/json")
    token_ <- get("token", thisEnv)
    if (token_ != "") {
      headers <- c(
        headers,
        setNames(glue::glue("Token {token_}"), "Authorization")
      )
    }
    return(httr::add_headers(.headers=headers))
  }
  handle_response_ = function(response){
    status <- response$status_code
    if (status >= 400 & status < 500) {
      content_txt <- httr::content(response, as="text")
      stop(glue::glue("<{status}>: {content_txt}")) }
    else if (status == 500) {
      stop(glue::glue("<{status}>: {HAWC_SERVER_ERROR_}")) }
    else {
      return(httr::content(response))
    }
  }
  get_ = function(url) {
    response <- httr::GET(url, headers_())
    return(handle_response_(response))
  }
  post_ = function(url, ...) {
    response <- httr::POST(url, headers_(), ...)
    return(handle_response_(response))
  }
  patch_ = function(url, ...) {
    response <- httr::PATCH(url, headers_(), ...)
    return(handle_response_(response))
  }
  delete_ = function(url, ...) {
    response <- httr::DELETE(url, headers_(), ...)
    return(handle_response_(response))
  }
  as_data_frame = function(response.list) {
    response.list = lapply(response.list, lapply, function(x)ifelse(is.null(x), NA, x))
    response.df = plyr::rbind.fill(lapply(response.list, as.data.frame))
    return(response.df)
  }
  iter_pages = function(url) {
    response_json = get_(url)
    results_list = response_json$results
    # Prevents divide by zero if there are no results
    if (length(response_json$results) == 0) {
      return()
    }
    # Set up progress bar
    num_pages = ceiling(response_json$count / length(response_json$results))
    pb <- txtProgressBar(min = 0, max = num_pages, style = 3)
    Sys.sleep(0.1)
    i = 2
    while (!(is.null(response_json$`next`))) {
      response_json = get_(response_json$`next`)
      results_list = append(results_list, response_json$results)
      setTxtProgressBar(pb, i)
      i = i+1
    }
    close(pb)
    return (results_list)
  }

  # public methods exposed by client
  public = list(
    version__ = "2020.7",
    authenticate = function(username, password){
      response = post_(
        glue::glue(root_url, "/user/api/token-auth/"),
        body = list(username = username, password = password),
        encode = "json"
      )
      token = response[[1]]
      assign("token", token, thisEnv)
    },

    # assessment
    assessment_public = function(){
      url = glue::glue("{root_url}/assessment/api/assessment/public/")
      response = get_(url)
      return(response)
    },
    assessment_bioassay_ml_dataset = function(){
      url = glue::glue("{root_url}/assessment/api/assessment/bioassay_ml_dataset/")
      response = get_(url)
      return(as_data_frame(response))
    },

    # literature
    lit_import_hero = function(assessment_id, title, description, ids) {
      url = glue::glue("{root_url}/lit/api/search/")
      pc_json = list(
        assessment = assessment_id,
        search_type = "i",
        source = 2,
        title = title,
        description = description,
        search_string = paste(unlist(ids), collapse=",")
      )
      response = post_(url, body = pc_json, encode = "json")
      return(response)
    },
    lit_tags = function(assessment_id) {
      url = glue::glue("{root_url}/lit/api/assessment/{assessment_id}/tags/")
      response = get_(url)
      return(as_data_frame(response))
    },
    lit_reference_tags = function(assessment_id) {
      url = glue::glue("{root_url}/lit/api/assessment/{assessment_id}/reference-tags/")
      response = get_(url)
      return(as_data_frame(response))
    },
    lit_import_reference_tags = function(assessment_id, csv, operation = "append") {
      url = glue::glue("{root_url}/lit/api/assessment/{assessment_id}/reference-tags/")
      response = post_(
        url,
        body = list(csv = csv, operation = operation),
        encode = "json"
      )
      return(as_data_frame(response))
    },
    lit_reference_ids = function(assessment_id) {
      url = glue::glue("{root_url}/lit/api/assessment/{assessment_id}/reference-ids/")
      response = get_(url)
      return(as_data_frame(response))
    },
    lit_references = function(assessment_id) {
      url = glue::glue("{root_url}/lit/api/assessment/{assessment_id}/references-download/")
      response = get_(url)
      return(as_data_frame(response))
    },
    lit_reference = function(reference_id){
      url = glue::glue("{root_url}/lit/api/reference/{reference_id}/")
      response = get_(url)
      return(response)
    },
    lit_update_reference = function(reference_id, data){
      url = glue::glue("{root_url}/lit/api/reference/{reference_id}/")
      response = patch_(url, body = data, encode = "json")
      return(response)
    },
    lit_delete_reference = function(reference_id){
      url = glue::glue("{root_url}/lit/api/reference/{reference_id}/")
      response = delete_(url)
      return(response)
    },

    # risk of bias
    rob_data = function(assessment_id) {
      url = glue::glue("{root_url}/rob/api/assessment/{assessment_id}/export/")
      response = get_(url)
      return(as_data_frame(response))
    },
    rob_full_data = function(assessment_id) {
      url = glue::glue("{root_url}/rob/api/assessment/{assessment_id}/full-export/")
      response = get_(url)
      return(as_data_frame(response))
    },
    rob_create = function(data) {
      stop(NOT_IMPLEMENTED_ERROR_)
    },

    # study
    study_create = function(reference_id, short_citation, full_citation, data) {
      if (is.null(data)){
        data = list();
      }
      data[['reference_id']] = reference_id
      data[['short_citation']] = short_citation
      data[['full_citation']] = full_citation
      url = glue::glue("{root_url}/study/api/study/")
      response = post_(url, body = data, encode = "json")
      return(response)
    },

    # animal bioassay
    ani_data = function(assessment_id) {
      url = glue::glue("{root_url}/ani/api/assessment/{assessment_id}/full-export/")
      response = get_(url)
      return(as_data_frame(response))
    },
    ani_data_summary = function(assessment_id) {
      url = glue::glue("{root_url}/ani/api/assessment/{assessment_id}/endpoint-export/")
      response = get_(url)
      return(as_data_frame(response))
    },
    ani_endpoints = function(assessment_id) {
      assessment_id = assessment_id
      url = glue::glue("{root_url}/ani/api/endpoint/?assessment_id={assessment_id}")
      generator = iter_pages(url)
      return(generator) #** doesnt match python version yet
    },
    ani_create_experiment = function(data) {
      url = glue::glue("{root_url}/ani/api/experiment/")
      response = post_(url, body = data, encode = "json")
      return(response)
    },
    ani_create_animal_group = function(data) {
      url = glue::glue("{root_url}/ani/api/animal-group/")
      response = post_(url, body = data, encode = "json")
      return(response)
    },
    ani_create_endpoint = function(data) {
      url = glue::glue("{root_url}/ani/api/endpoint/")
      response = post_(url, body = data, encode = "json")
      return(response)
    },

    # epidemiology
    epi_data = function(assessment_id) {
      url = glue::glue("{root_url}/epi/api/assessment/{assessment_id}/export/")
      response = get_(url)
      return(as_data_frame(response))
    },
    epi_endpoints = function(assessment_id) {
      assessment_id = assessment_id
      url = glue::glue("{root_url}/epi/api/outcome/?assessment_id={assessment_id}")
      generator = iter_pages(url)
      return(generator) #** doesnt match python version yet
    },

    # epidemiology meta-analyses
    epimeta_data = function(assessment_id) {
      url = glue::glue("{root_url}/epi-meta/api/assessment/{assessment_id}/export/")
      response = get_(url)
      return(as_data_frame(response))
    },

    # invitro
    invitro_data = function(assessment_id) {
      url = glue::glue("{root_url}/in-vitro/api/assessment/{assessment_id}/full-export/")
      response = get_(url)
      return(as_data_frame(response))
    },

    # summary
    visual_list = function(assessment_id) {
      url = glue::glue("{root_url}/summary/api/visual/?assessment_id={assessment_id}")
      response = get_(url)
      return(as_data_frame(response))
    }
  )

  # package things up and return public API with scoped helper methods
  assign("this", public, envir=thisEnv)
  class(public) = append(class(public), "HawcClient")
  return(public)
}
