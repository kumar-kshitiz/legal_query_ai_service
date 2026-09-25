from datetime import (
    datetime,
    timezone,
    timedelta,
)

from typing import Any


class LegalFreshnessChecker:

    def __init__(
        self,
        now: datetime | None = None
    ):

        self.now = (
            now
            if now is not None
            else datetime.now(
                timezone.utc
            )
        )


    # ==============================================
    # Date parser
    # ==============================================

    def parse_datetime(
        self,
        value: str | None
    ) -> datetime | None:

        if not value:

            return None


        value = value.strip()


        # ------------------------------------------
        # Handle YYYY-MM-DD
        # ------------------------------------------

        try:

            dt = datetime.strptime(
                value,
                "%Y-%m-%d"
            )


            return dt.replace(
                tzinfo=timezone.utc
            )

        except ValueError:

            pass


        # ------------------------------------------
        # Handle ISO format
        # ------------------------------------------

        try:

            value = value.replace(
                "Z",
                "+00:00"
            )


            dt = datetime.fromisoformat(
                value
            )


            if dt.tzinfo is None:

                dt = dt.replace(
                    tzinfo=timezone.utc
                )


            return dt.astimezone(
                timezone.utc
            )

        except ValueError:

            return None


    # ==============================================
    # Status
    # ==============================================

    def check_status(
        self,
        metadata: dict[str, Any]
    ) -> tuple[bool, str]:

        status = str(
            metadata.get(
                "status",
                ""
            )
        ).lower()


        if status != "active":

            return (
                False,
                f"Document status is '{status}'."
            )


        return (
            True,
            "Document is active."
        )


    # ==============================================
    # Verification
    # ==============================================

    def check_verified(
        self,
        metadata: dict[str, Any]
    ) -> tuple[bool, str]:

        verified = bool(
            metadata.get(
                "verified",
                False
            )
        )


        if not verified:

            return (
                False,
                "Document is not verified."
            )


        return (
            True,
            "Document is verified."
        )


    # ==============================================
    # Effective date
    # ==============================================

    def check_effective_dates(
        self,
        metadata: dict[str, Any]
    ) -> tuple[bool, str]:

        effective_from = (
            self.parse_datetime(
                metadata.get(
                    "effective_from"
                )
            )
        )


        effective_to = (
            self.parse_datetime(
                metadata.get(
                    "effective_to"
                )
            )
        )


        if (
            effective_from is not None
            and
            self.now < effective_from
        ):

            return (
                False,
                "Document is not effective yet."
            )


        if (
            effective_to is not None
            and
            self.now > effective_to
        ):

            return (
                False,
                "Document is no longer effective."
            )


        return (
            True,
            "Effective date is valid."
        )


    # ==============================================
    # Source freshness
    # ==============================================

    def check_source_freshness(
        self,
        metadata: dict[str, Any]
    ) -> tuple[bool, str]:

        last_checked = (
            self.parse_datetime(
                metadata.get(
                    "last_checked_at"
                )
                or
                metadata.get(
                    "source_last_checked_at"
                )
            )
        )


        if last_checked is None:

            return (
                False,
                "Official source has never been "
                "freshness-checked."
            )


        frequency_hours = int(
            metadata.get(
                "check_frequency_hours",
                168
            )
        )


        maximum_age = timedelta(
            hours=frequency_hours
        )


        age = (
            self.now
            -
            last_checked
        )


        if age > maximum_age:

            hours_old = (
                age.total_seconds()
                / 3600
            )


            return (
                False,
                (
                    "Official source check is stale "
                    f"({hours_old:.1f} hours old)."
                )
            )


        return (
            True,
            "Official source freshness is valid."
        )


    # ==============================================
    # Content hash
    # ==============================================

    def check_content_hash(
        self,
        metadata: dict[str, Any]
    ) -> tuple[bool, str]:

        content_hash = metadata.get(
            "content_hash"
        )


        if not content_hash:

            return (
                False,
                "Document has no content hash."
            )


        if len(
            str(
                content_hash
            )
        ) != 64:

            return (
                False,
                "Document content hash is invalid."
            )


        return (
            True,
            "Content hash is present."
        )


    # ==============================================
    # Complete validation
    # ==============================================

    def validate(
        self,
        metadata: dict[str, Any]
    ) -> dict[str, Any]:

        checks = {}


        checks[
            "status"
        ] = self.check_status(
            metadata
        )


        checks[
            "verified"
        ] = self.check_verified(
            metadata
        )


        checks[
            "effective_dates"
        ] = self.check_effective_dates(
            metadata
        )


        checks[
            "source_freshness"
        ] = self.check_source_freshness(
            metadata
        )


        checks[
            "content_hash"
        ] = self.check_content_hash(
            metadata
        )


        eligible = all(

            result[0]

            for result
            in checks.values()
        )


        return {

            "document_id":
                metadata.get(
                    "document_id"
                ),

            "law_id":
                metadata.get(
                    "law_id"
                ),

            "version":
                metadata.get(
                    "version"
                ),

            "eligible_for_retrieval":
                eligible,

            "checks": {

                name: {

                    "passed":
                        result[0],

                    "message":
                        result[1]

                }

                for name, result
                in checks.items()
            }
        }