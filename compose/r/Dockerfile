FROM rocker/r-ver:4.0.3
# https://github.com/rocker-org/rocker-versioned2/blob/master/dockerfiles/Dockerfile_r-ver_4.0.3
# https://github.com/rstudio/plumber/blob/master/Dockerfile

# BEGIN rstudio/plumber layers
RUN apt-get update -qq && apt-get install -y --no-install-recommends \
    git-core \
    libssl-dev \
    libcurl4-gnutls-dev \
    curl \
    libsodium-dev \
    libxml2-dev

RUN groupadd -g 555 -r app && \
    useradd app -u 555 -r -g app -G staff

USER app

COPY dist/hawc_0.1.0.tar.gz /home/app/hawc_0.1.0.tar.gz
RUN R -e "install.packages('remotes')" && \
    R -e "remotes::install_local('/home/app/hawc_0.1.0.tar.gz', dependencies=T)"

EXPOSE 5010
CMD ["R", "-e", "hawc::httpApi$run(host = '0.0.0.0', port = 5010)"]
