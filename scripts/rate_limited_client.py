import threading  # Provides a lock so multiple Streamlit sessions cannot call the client at the same time.
import time  # Provides monotonic timing and sleep.


class RateLimitedClient:  # Wraps another client and slows down calls to its invoke method.
    def __init__(self, client, min_interval_seconds=1.0):  # Receive the real client and the minimum wait time.
        self.client = client  # Store the real ChatMistralAI client.
        self.min_interval_seconds = min_interval_seconds  # Store the required pause between calls.
        self._last_call_finished_at = 0.0  # Track when the previous invoke call finished.
        self._lock = threading.Lock()  # Ensure only one thread/session enters invoke at a time.

    def invoke(self, *args, **kwargs):  # Expose the same invoke method used by ChatMistralAI.
        with self._lock:  # Serialize calls so the wait is enforced globally for this wrapper object.
            elapsed = time.monotonic() - self._last_call_finished_at  # Measure time since the previous call finished.
            wait_seconds = self.min_interval_seconds - elapsed  # Calculate how much longer to wait.

            if wait_seconds > 0:  # Only sleep if the previous call finished too recently.
                time.sleep(wait_seconds)  # Pause before starting the next provider call.

            result = self.client.invoke(*args, **kwargs)  # Call the real ChatMistralAI client.
            self._last_call_finished_at = time.monotonic()  # Save the finish time for the next call.
            return result  # Return the original LLM response unchanged.

    def __getattr__(self, name):  # Forward any other attribute access to the wrapped client.
        return getattr(self.client, name)  # Preserve compatibility if other code reads client attributes.