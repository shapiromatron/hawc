#' The main webservice HTTP entrypoint
#'
#' In addition to standard function-endpoints for methods included in hawc, we also include a
#' REST HTTP API for execution of these methods. This is the main entrypoint for the HTTP routing
#' function. When using the `$run()` method on this object, a webserver process will start and
#' listen for incoming requests on the port specified. A swagger API is also available. For more
#' details, refer to documentation in the plumber package.
#'
#' @import plumber
#' @export
httpApi <- plumber::pr()

httpApi$handle("GET", "/api/v1/healthcheck/", function(){
    response <- list(status = "marco polo");
    return(response);
}, serializer=plumber::serializer_unboxed_json())


httpApi$handle("POST", "/api/v1/sum/", function(a, b) {
    resp <- sillySum(a,b)
    response <- list(result = resp);
    return(response);

}, serializer=plumber::serializer_unboxed_json())


httpApi$handle("GET", "/api/v1/plot/", function(spec){
    myData <- iris
    title <- "All Species"
    # Filter if the species was specified
    if (!missing(spec)){
        title <- paste0("Only the '", spec, "' Species")
        myData <- subset(iris, Species == spec)
    }
    plot(
        myData$Sepal.Length, myData$Petal.Length, main=title,
        xlab="Sepal Length", ylab="Petal Length"
    )
}, serializer=plumber::serializer_pdf())
