# Deployment

Minimum hardware requirements:

- Linux
- 8 GB RAM (16 GB recommended)
- 2 processors (4-8 recommended)
- 100 GB HD space (SSD preferred)

Software requirements:

- docker and docker compose
- [fabric](http://www.fabfile.org/) is used for (semi) automated deployment; contact if you're interested and we can share ...

HAWC has been deployed in the past on a bare-VM, using containers with docker-compose (recommended), on AWS with RDS, and in kubernetes. If you're looking for discussion deployment options, contact us!

## Build and deploy

Build docker containers which can be deployed. These can be pushed to a container registry or
other approaches for sharing with the deployment target:

```bash
# build containers (in the hawc development environment)
source venv/bin/activate
make build
docker-compose -f compose/dc-build.yml --project-directory . build
```

To test-deploy the containers on your development computer:

```bash
# go to a new directory
cd ~/dev/temp
mkdir -p hawc-deploy
cd hawc-deploy

# make shared volumes
mkdir -p data/postgres/backups
mkdir -p data/public
mkdir -p data/private
mkdir -p data/nginx

# copy deployment settings
cp ~/dev/hawc/compose/nginx/conf/nginx.example.conf ./data/nginx/nginx.conf
cp ~/dev/hawc/compose/dc-deploy.yml ./docker-compose.yml
cp ~/dev/hawc/compose/example.env ./.env

# start containers, order is important
# ... start the backend services
docker-compose up -d redis postgres
# ... one time filesystem/database changes
docker-compose run --no-deps --rm sync
# ... start applications
docker-compose up -d web workers cron nginx

# should be running, a few example commands for testing
# check static files
curl -I http://127.0.0.1:8000/static/css/hawc.css
# check django request
curl -I http://127.0.0.1:8000/user/login/
docker-compose exec web manage createsuperuser
docker-compose logs -f

# shut down containers
docker-compose down
```

The same approach can be done in production, except please harden the deployment :) .

## Configuration

For configurable parameters, we use environment variables which are loaded in the application configuration at runtime.  See the example [configuration file](https://github.com/shapiromatron/hawc/blob/main/compose/example.env) for a complete example. Many variables directly map to settings which are commonly used in django; refer to django documentation for these settings. Additional details on HAWC-specific variables are described below:

- `HAWC_ANYONE_CAN_CREATE_ASSESSMENTS` [True/False; default True]. If true, anyone can create a new assessment. If false, only those who are added to the `can-create-assessments` group by system administrators can create a new assessment.
- `HAWC_PM_CAN_MAKE_PUBLIC` [True/False; default True].  If true, assessment project managers have the ability to make an assessment public (and editable) on the HAWC website. If false, only administrators can make assessments public.
- `HAWC_INCLUDE_ADMIN` [True/False, default True]. If true, the admin is included in the hawc deployment. If false, it's not included. In some deployments, the admin may be deployed separately with additional security.
- `HAWC_SESSION_DURATION` [int, default 604800 seconds or 1 week]. The length of a HAWC user-session. After this duration is exceeded, the user must login for a new session.
- `HAWC_AUTH_PROVIDERS` [pipe-separated str of hawc.constants.AuthProvider, default "django"]. A list of providers which can be used for authentication. One or more providers can be used and pipe separated.
    - The "django" authentication provider means accounts can be created in hawc and passwords are managed in hawc
    - The "external" authentication provider assumes an upstream server handles authentication and returns appropriate user metadata for integration via `/user/login/wam/`.  If used, `hawc.apps.myuser.views.ExternalAuth.get_user_metadata` requires a custom implementation.
- `HAWC_LOGOUT_REDIRECT` [str, optional]. URL to redirect to after logout. Defaults to the homepage of hawc; this may need to be modified with some authentication providers.
- `HAWC_LOAD_TEST_DB` [0/1; default 0]. Load a test database with pre-populated fake data (1), or never ( default). This setting is only used in staging and production django settings.

### Feature flags

Some configurations are behind an environment variable in JSON form, `HAWC_FEATURE_FLAGS`. To set these options, you'll need to set the variable to valid JSON as an environment variable. For example:

```bash
export HAWC_FEATURE_FLAGS='{"THIS_IS_AN_EXAMPLE":true}'
```

Fields include:

- `THIS_IS_AN_EXAMPLE`: Does nothing; used to test configuration.
- `DEFAULT_LITERATURE_CONFLICT_RESOLUTION`: If true, when a new assessment is created, conflict resolution is enabled. If false, its disabled. Defaults to false.
- `ALLOW_RIS_IMPORTS`: If true, RIS imports are available when working on assessments. If false, the button is not there, but it's still possible for users to import via RIS if the can find the correct URL. Defaults to true.
- `ANONYMOUS_ACCOUNT_CREATION`: If true, anonymous users can create accounts. If false, only staff can create new accounts via the admin. Defaults to true.
- `ENABLE_BMDS_33`: If true, enable BMD execution using 3.x versions, currently under  development. Defaults to false.

### Application monitoring

Application performance and monitoring can be optionally enabled using [Sentry](https://sentry.io/). To enable, add these two environment variables:

- `HAWC_SENTRY_DSN` - site key, used for sentry data ingestion
- `HAWC_SENTRY_SETTINGS`: JSON string of settings to pass to [client](https://docs.sentry.io/platforms/python/guides/django/configuration/options/), for example: `{"traces_sample_rate": 0.1, "send_default_pii": false}`

By default, sentry integration is disabled.

### Human verification

To prevent bots from attempting to login to the server, you can optionally enable [Turnstyle](https://www.cloudflare.com/products/turnstile/). To enable, set these two additional environment variables:

- `TURNSTYLE_SITE`: site key, this is used by the client to interact (public)
- `TURNSTYLE_KEY`: secret key, used by the server to verify the response (private)

By default. human verification is disabled.
