"""
Amazon S3 Cloud Synchronization for OmniMCP Assistant.

Allows users to back up and synchronize everyday state (notes, grocery lists,
calendar, budget logs, and memory) to a personal or team S3 bucket.
"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("OmniMCP.AWS.S3")


class S3CloudSync:
    """Manages cloud backup and state restore via Amazon Simple Storage Service (S3)."""

    def __init__(self, bucket_name: Optional[str] = None):
        self.bucket_name = bucket_name or os.environ.get("AWS_S3_SYNC_BUCKET")
        self._s3 = None
        self._init_s3()

    def _init_s3(self):
        try:
            import boto3
            self._s3 = boto3.client("s3")
        except Exception as e:
            self._s3 = None
            logger.info("boto3 not active for S3 sync (%s). Local state preserved.", e)

    def is_configured(self) -> bool:
        return self._s3 is not None and bool(self.bucket_name)

    def backup_everyday_data(self, local_dir: Path) -> Dict[str, Any]:
        """Uploads JSON state files from local_dir to S3 bucket."""
        if not self.is_configured():
            return {"status": "skipped", "message": "S3 bucket not configured or boto3 absent."}

        uploaded = []
        try:
            for file_path in local_dir.glob("*.json"):
                key = f"omnimcp-data/{file_path.name}"
                self._s3.upload_file(str(file_path), self.bucket_name, key)
                uploaded.append(file_path.name)
            return {"status": "success", "uploaded_files": uploaded, "count": len(uploaded)}
        except Exception as e:
            logger.error("S3 upload failed: %s", e)
            return {"status": "error", "message": str(e)}

    def restore_everyday_data(self, target_dir: Path) -> Dict[str, Any]:
        """Downloads backed-up state files from S3 to target_dir."""
        if not self.is_configured():
            return {"status": "skipped", "message": "S3 bucket not configured or boto3 absent."}

        target_dir.mkdir(parents=True, exist_ok=True)
        downloaded = []
        try:
            resp = self._s3.list_objects_v2(Bucket=self.bucket_name, Prefix="omnimcp-data/")
            contents = resp.get("Contents", [])
            for item in contents:
                key = item["Key"]
                filename = Path(key).name
                dest = target_dir / filename
                self._s3.download_file(self.bucket_name, key, str(dest))
                downloaded.append(filename)
            return {"status": "success", "downloaded_files": downloaded, "count": len(downloaded)}
        except Exception as e:
            logger.error("S3 download failed: %s", e)
            return {"status": "error", "message": str(e)}
