"""Selenium session manager for 'Teaching' AutoCPD new portals."""

from __future__ import annotations

import os
import time
import threading
from typing import Callable, Dict, Optional

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


class PortalMapper:
    """Orchestrates the interactive mapping session in a browser.
    
    Injects a JS HUD that allows the user to click elements and confirm 
    them as mapping targets for specific CPD data fields.
    """

    FIELDS = [
        "Title",
        "Date",
        "Hours",
        "Category",
        "Notes",
        "Evidence Upload Button"
    ]

    def __init__(self, url: str, log_callback: Optional[Callable[[str], None]] = None):
        self.url = url
        self._log = log_callback
        self._driver: Optional[webdriver.Chrome] = None
        self._mapping: Dict[str, str] = {}
        self._is_running = False
        self._script_path = os.path.join(os.path.dirname(__file__), "mapping_script.js")

    def _emit_log(self, msg: str):
        if self._log:
            self._log(msg)

    def start(self, on_complete: Optional[Callable[[Dict[str, str]], None]] = None):
        """Run the mapping session in a background thread."""
        thread = threading.Thread(target=self._run_session, args=(on_complete,), daemon=True)
        thread.start()

    def _ensure_script_injected(self) -> bool:
        """Check if the HUD is present in the current DOM; if not, re-inject it."""
        try:
            is_active = self._driver.execute_script(
                "return typeof window._autocpd_mapping_active !== 'undefined' && window._autocpd_mapping_active;"
            )
            if not is_active:
                with open(self._script_path, "r", encoding="utf-8") as f:
                    script = f.read()
                self._driver.execute_script(script)
                return True
        except:
            return False
        return True

    def _run_session(self, on_complete: Optional[Callable[[Dict[str, str]], None]]):
        self._is_running = True
        self._emit_log(f"Launching browser mapping session for: {self.url}")
        
        chrome_options = Options()
        try:
            service = ChromeService(ChromeDriverManager().install())
            self._driver = webdriver.Chrome(service=service, options=chrome_options)
            self._driver.get(self.url)
            
            # 1. Wait Phase: User navigates / logs in
            self._emit_log("Waiting for user to navigate and click 'I am Ready' in-browser...")
            while self._is_running:
                if not self._ensure_script_injected():
                    # If driver is closed or invalid
                    break
                
                ready = self._driver.execute_script("return window._autocpd_is_ready;")
                if ready:
                    self._emit_log("User signaled READY. Starting field sequence...")
                    break
                time.sleep(1.0)

            # 2. Sequential Mapping Loop
            for field in self.FIELDS:
                if not self._is_running: break
                
                self._emit_log(f"Searching for: {field}...")
                self._ensure_script_injected()
                self._driver.execute_script(f"window._autocpd_set_target('{field}');")
                
                # Polling for confirmation or skip
                confirmed_selector = None
                while self._is_running:
                    try:
                        self._ensure_script_injected()
                        result = self._driver.execute_script("""
                            return {
                                selector: window._autocpd_verified_selector,
                                skipped: window._autocpd_skipped
                            };
                        """)
                        
                        if result["skipped"]:
                            self._emit_log(f"Skipped field: {field}")
                            break
                        
                        if result["selector"]:
                            confirmed_selector = result["selector"]
                            self._mapping[field] = confirmed_selector
                            self._emit_log(f"Mapped {field} -> {confirmed_selector}")
                            break
                            
                    except Exception as e:
                        self._emit_log(f"Mapping interrupted: {e}")
                        self._is_running = False
                        break
                        
                    time.sleep(0.5)
            
            if self._is_running:
                self._emit_log("Mapping session complete! Closing browser...")
                time.sleep(2) # brief pause for the user to see the last confirm
                
        except Exception as e:
            self._emit_log(f"Error during mapping: {str(e)}")
        finally:
            if self._driver:
                try:
                    self._driver.quit()
                except:
                    pass
            self._is_running = False
            if on_complete:
                on_complete(self._mapping)

    def stop(self):
        """Force stop the mapping session."""
        self._is_running = False
        if self._driver:
            try:
                self._driver.quit()
            except:
                pass
