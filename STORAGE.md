# File Storage Configuration

HAWC supports configurable file storage backends for static and media files. By default, files are stored on the local filesystem, but S3-compatible storage can be enabled via environment variables.

## Default Filesystem Storage

When no additional configuration is provided, HAWC uses Django's default filesystem storage:

- Static files: `/static/` URL path, stored in `{PUBLIC_DATA_ROOT}/static/`
- Media files: `/media/` URL path, stored in `{PUBLIC_DATA_ROOT}/media/`

## S3-Compatible Storage

To enable S3 storage, set the following environment variables:

### Required Variables

- `HAWC_USE_S3_STORAGE`: Set to `"true"` to enable S3 storage
- `AWS_ACCESS_KEY_ID`: Your AWS access key ID
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret access key
- `AWS_STORAGE_BUCKET_NAME`: The S3 bucket name to use

### Optional Variables

- `AWS_S3_REGION_NAME`: AWS region (default: "us-east-1")
- `AWS_S3_CUSTOM_DOMAIN`: Custom domain for CDN (e.g., "cdn.example.com")
- `AWS_S3_ENDPOINT_URL`: Custom S3 endpoint for S3-compatible services (e.g., MinIO)
- `AWS_S3_USE_SSL`: Use HTTPS (default: "True")
- `AWS_S3_VERIFY`: Verify SSL certificates (default: "True")
- `AWS_QUERYSTRING_AUTH`: Include auth in URLs (default: "False")
- `AWS_S3_FILE_OVERWRITE`: Allow file overwriting (default: "True")
- `AWS_DEFAULT_ACL`: Default ACL for uploaded files (default: "public-read")

## Examples

### Basic AWS S3 Configuration

```bash
export HAWC_USE_S3_STORAGE=true
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_STORAGE_BUCKET_NAME=my-hawc-bucket
export AWS_S3_REGION_NAME=us-west-2
```

### S3 with CloudFront CDN

```bash
export HAWC_USE_S3_STORAGE=true
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_STORAGE_BUCKET_NAME=my-hawc-bucket
export AWS_S3_CUSTOM_DOMAIN=cdn.example.com
```

### MinIO (S3-Compatible)

```bash
export HAWC_USE_S3_STORAGE=true
export AWS_ACCESS_KEY_ID=minio_access_key
export AWS_SECRET_ACCESS_KEY=minio_secret_key
export AWS_STORAGE_BUCKET_NAME=hawc-storage
export AWS_S3_ENDPOINT_URL=https://minio.example.com
export AWS_S3_USE_SSL=true
```

## File Organization

When using S3 storage, files are organized as follows:

- Static files: `{bucket}/static/`
- Media files: `{bucket}/media/`

## Security Notes

- Private data storage (configured via `PRIVATE_DATA_ROOT`) always uses local filesystem storage for security
- When using S3, ensure your bucket permissions are properly configured
- Consider using IAM roles instead of access keys when running on AWS
- For production deployments, consider using a CDN for better performance