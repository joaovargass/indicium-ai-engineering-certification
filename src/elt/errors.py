"""Custom exceptions for ELT pipeline. ELTError carries stage and message for UI display."""


class ELTError(Exception):
    """Raised when an ELT stage fails. stage and message are used by elt_callbacks to show [stage]: message."""

    def __init__(self, stage: str, message: str) -> None:
        """Store stage and message for UI display and set Exception message to [stage]: message."""
        self.stage = stage
        self.message = message
        super().__init__(f"[{stage}] {message}")
