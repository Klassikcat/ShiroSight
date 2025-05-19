import boto3
import logging


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class S3Uploader:
    def __init__(self, profile_name: str):
        self.session = boto3.Session(profile_name=profile_name)
        self.client = self.session.client("s3")

    def upload_file(self, bucket_name: str, file_path: str, key: str):
        self.client.upload_file(file_path, bucket_name, key)
        logger.info(f"Uploaded file to S3: {file_path} -> {bucket_name}/{key}")