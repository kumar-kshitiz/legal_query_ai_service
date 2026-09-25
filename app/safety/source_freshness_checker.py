import hashlib

from datetime import (
    datetime,
    timedelta,
    timezone,
)

from typing import Any

import requests


class OfficialSourceChecker:

    def __init__(
        self,
        timeout_seconds: int = 30
    ):

        self.timeout_seconds = (
            timeout_seconds
        )


    # ==============================================
    # Current UTC timestamp
    # ==============================================

    def now_iso(
        self
    ) -> str:

        return (
            datetime.now(
                timezone.utc
            )
            .isoformat()
        )


    # ==============================================
    # SHA-256 remote content
    # ==============================================

    def hash_remote_file(
        self,
        url: str
    ) -> tuple[
        str,
        dict[str, Any]
    ]:

        response = requests.get(

            url,

            stream=True,

            timeout=self.timeout_seconds,

            allow_redirects=True,

            headers={
                "User-Agent":
                    "LegalQueryPlatform/1.0"
            }
        )


        response.raise_for_status()


        content_type = (

            response.headers.get(
                "Content-Type",
                ""
            )
            .lower()

        )


        # ------------------------------------------
        # Protection against accidentally hashing
        # an HTML error/login page instead of PDF
        # ------------------------------------------

        if (
            "text/html"
            in content_type
        ):

            raise ValueError(
                "Official source returned HTML "
                "instead of the legal document."
            )


        sha256 = hashlib.sha256()


        total_bytes = 0


        for chunk in response.iter_content(
            chunk_size=8192
        ):

            if not chunk:

                continue


            sha256.update(
                chunk
            )


            total_bytes += len(
                chunk
            )


        if total_bytes == 0:

            raise ValueError(
                "Official source returned "
                "an empty document."
            )


        headers = {

            "etag":
                response.headers.get(
                    "ETag"
                ),

            "last_modified":
                response.headers.get(
                    "Last-Modified"
                ),

            "content_type":
                response.headers.get(
                    "Content-Type"
                ),

            "content_length":
                response.headers.get(
                    "Content-Length"
                ),

            "final_url":
                response.url,

            "downloaded_bytes":
                total_bytes,
        }


        return (
            sha256.hexdigest(),
            headers
        )


    # ==============================================
    # Verify official source
    # ==============================================

    def verify(
        self,
        metadata: dict[str, Any]
    ) -> dict[str, Any]:

        source_url = metadata.get(
            "source_url"
        )


        local_hash = metadata.get(
            "content_hash"
        )


        if not source_url:

            return {

                "success":
                    False,

                "changed":
                    None,

                "message":
                    "source_url is missing."
            }


        if not local_hash:

            return {

                "success":
                    False,

                "changed":
                    None,

                "message":
                    "Stored content_hash is missing."
            }


        try:

            remote_hash, headers = (
                self.hash_remote_file(
                    source_url
                )
            )


        except Exception as e:

            return {

                "success":
                    False,

                "changed":
                    None,

                "message":
                    str(e)
            }


        changed = (

            remote_hash.lower()
            !=
            str(
                local_hash
            ).lower()

        )


        return {

            "success":
                True,

            "changed":
                changed,

            "local_hash":
                local_hash,

            "remote_hash":
                remote_hash,

            "headers":
                headers,

            "message":
                (
                    "Official source matches "
                    "stored document."
                    if not changed
                    else
                    "Official source content "
                    "has changed."
                )
        }


    # ==============================================
    # Apply successful freshness result
    # ==============================================

    def apply_result(
        self,
        metadata: dict[str, Any],
        result: dict[str, Any]
    ) -> dict[str, Any]:

        # ------------------------------------------
        # Never update freshness if verification
        # itself failed
        # ------------------------------------------

        if not result.get(
            "success"
        ):

            return metadata


        now = datetime.now(
            timezone.utc
        )


        now_string = (
            now.isoformat()
        )


        frequency_hours = int(
            metadata.get(
                "check_frequency_hours",
                168
            )
        )


        next_check = (

            now
            +
            timedelta(
                hours=frequency_hours
            )

        )


        headers = result.get(
            "headers",
            {}
        )


        # ------------------------------------------
        # Source metadata
        # ------------------------------------------

        metadata[
            "source_etag"
        ] = headers.get(
            "etag"
        )


        metadata[
            "source_last_modified"
        ] = headers.get(
            "last_modified"
        )


        metadata[
            "source_last_checked_at"
        ] = now_string


        metadata[
            "last_checked_at"
        ] = now_string


        metadata[
            "next_check_at"
        ] = (
            next_check.isoformat()
        )


        # ==========================================
        # SAME DOCUMENT
        # ==========================================

        if not result.get(
            "changed"
        ):

            metadata[
                "source_change_detected"
            ] = False


            metadata[
                "pending_source_hash"
            ] = None


            metadata[
                "pending_review_required"
            ] = False


            return metadata


        # ==========================================
        # DOCUMENT CHANGED
        #
        # IMPORTANT:
        # Do not automatically replace our
        # active verified legal document.
        # ==========================================

        metadata[
            "source_change_detected"
        ] = True


        metadata[
            "pending_source_hash"
        ] = result.get(
            "remote_hash"
        )


        metadata[
            "pending_review_required"
        ] = True


        metadata[
            "last_changed_at"
        ] = now_string


        return metadata