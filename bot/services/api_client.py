"""
LMS API client.

Makes HTTP requests to the backend with Bearer token authentication.
"""

import httpx

from config import settings


class APIClient:
    """Client for the LMS backend API."""

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=10.0,
        )

    def get(self, endpoint: str) -> dict | list | None:
        """
        Make a GET request to the API.

        Args:
            endpoint: API endpoint (e.g., "/items/", "/analytics/pass-rates")

        Returns:
            JSON response or None if request fails.

        Raises:
            httpx.HTTPError: If request fails (caller should handle).
        """
        response = self._client.get(endpoint)
        response.raise_for_status()
        return response.json()

    def health_check(self) -> tuple[bool, str]:
        """
        Check if the backend is healthy.

        Returns:
            Tuple of (is_healthy, message).
        """
        try:
            data = self.get("/items/")
            count = len(data) if isinstance(data, list) else "unknown"
            return True, f"Backend is healthy. {count} items available."
        except httpx.ConnectError as e:
            return False, f"Backend error: connection refused ({self.base_url}). Check that the services are running."
        except httpx.HTTPStatusError as e:
            return False, f"Backend error: HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down."
        except httpx.HTTPError as e:
            return False, f"Backend error: {str(e)}"

    def get_labs(self) -> list[dict]:
        """
        Get list of available labs.

        Returns:
            List of lab objects with 'id', 'title', 'description'.
        """
        data = self.get("/items/")
        if not isinstance(data, list):
            return []
        # Filter only labs (type == "lab") from backend
        return [item for item in data if item.get("type") == "lab"]

    def get_pass_rates(self, lab_id: str) -> list[dict] | None:
        """
        Get pass rates for a specific lab.

        Args:
            lab_id: Lab identifier (e.g., "lab-04")

        Returns:
            List of task pass rates or None if not found.
        """
        try:
            data = self.get(f"/analytics/pass-rates?lab={lab_id}")
            return data if isinstance(data, list) else None
        except httpx.HTTPError:
            return None


# Global API client instance
api_client = APIClient(settings.lms_api_url, settings.lms_api_key)
