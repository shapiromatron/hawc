#' @import plumber
#' @export
httpApi <- plumber::pr()

httpApi$handle("GET", "/api/v1/healthcheck", function(){
    response <- list(status = "marco polo");
    response
}, serializer=plumber::serializer_unboxed_json())


httpApi$handle("POST", "/api/v1/sum", function(a, b) {
    resp <- sillySum(a,b)
    return(resp)
}, serializer=plumber::serializer_unboxed_json())


httpApi$handle("GET", "/api/v1/plot", function(spec){
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
