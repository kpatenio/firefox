# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import sys
import unittest

import marionette_driver.errors as errors
from marionette_harness import MarionetteTestCase


PROMPT_HANDLERS = [
    "accept",
    "accept and notify",
    "dismiss",
    "dismiss and notify",
    "ignore",
]

PROMPT_TYPES = [
    "alert",
    "beforeUnload",
    "confirm",
    "prompt",
]


class TestCapabilities(MarionetteTestCase):
    def setUp(self):
        super(TestCapabilities, self).setUp()
        self.caps = self.marionette.session_capabilities
        with self.marionette.using_context("chrome"):
            self.appinfo = self.marionette.execute_script(
                """
                return {
                  name: Services.appinfo.name,
                  version: Services.appinfo.version,
                  processID: Services.appinfo.processID,
                  buildID: Services.appinfo.appBuildID,
                }
                """
            )
            self.os_name = self.marionette.execute_script(
                """
                let name = Services.sysinfo.getProperty("name");
                switch (name) {
                  case "Windows_NT":
                    return "windows";
                  case "Darwin":
                    return "mac";
                  default:
                    return name.toLowerCase();
                }
                """
            )
            self.os_version = self.marionette.execute_script(
                "return Services.sysinfo.getProperty('version')"
            )

    def test_mandated_capabilities(self):
        self.assertIn("acceptInsecureCerts", self.caps)
        self.assertIn("browserName", self.caps)
        self.assertIn("browserVersion", self.caps)
        self.assertIn("platformName", self.caps)
        self.assertIn("proxy", self.caps)
        self.assertIn("setWindowRect", self.caps)
        self.assertIn("strictFileInteractability", self.caps)
        self.assertIn("timeouts", self.caps)

        self.assertFalse(self.caps["acceptInsecureCerts"])
        self.assertEqual(self.caps["browserName"], self.appinfo["name"].lower())
        self.assertEqual(self.caps["browserVersion"], self.appinfo["version"])
        self.assertEqual(self.caps["platformName"], self.os_name)
        self.assertEqual(self.caps["proxy"], {})

        if self.appinfo["name"] == "Firefox":
            self.assertTrue(self.caps["setWindowRect"])
        else:
            self.assertFalse(self.caps["setWindowRect"])
        self.assertTrue(self.caps["strictFileInteractability"])
        self.assertDictEqual(
            self.caps["timeouts"], {"implicit": 0, "pageLoad": 300000, "script": 30000}
        )

    def test_additional_capabilities(self):
        self.assertIn("moz:processID", self.caps)
        self.assertEqual(self.caps["moz:processID"], self.appinfo["processID"])
        self.assertEqual(self.marionette.process_id, self.appinfo["processID"])

        self.assertIn("moz:profile", self.caps)
        if self.marionette.instance is not None:
            if self.caps["browserName"] == "fennec":
                current_profile = (
                    self.marionette.instance.runner.device.app_ctx.remote_profile
                )
            else:
                current_profile = self.marionette.profile_path
            # Bug 1438461 - mozprofile uses lower-case letters even on case-sensitive filesystems
            # Bug 1533221 - paths may differ due to file system links or aliases
            self.assertEqual(
                os.path.basename(self.caps["moz:profile"]).lower(),
                os.path.basename(current_profile).lower(),
            )

        self.assertIn("moz:accessibilityChecks", self.caps)
        self.assertFalse(self.caps["moz:accessibilityChecks"])

        self.assertIn("moz:buildID", self.caps)
        self.assertEqual(self.caps["moz:buildID"], self.appinfo["buildID"])

        self.assertNotIn("moz:debuggerAddress", self.caps)

        self.assertIn("moz:platformVersion", self.caps)
        self.assertEqual(self.caps["moz:platformVersion"], self.os_version)

        self.assertIn("moz:webdriverClick", self.caps)
        self.assertTrue(self.caps["moz:webdriverClick"])

        self.assertIn("moz:windowless", self.caps)
        self.assertFalse(self.caps["moz:windowless"])

    def test_disable_webdriver_click(self):
        self.marionette.delete_session()
        self.marionette.start_session({"moz:webdriverClick": False})
        caps = self.marionette.session_capabilities
        self.assertFalse(caps["moz:webdriverClick"])

    def test_valid_uuid4_when_creating_a_session(self):
        self.assertNotIn(
            "{",
            self.marionette.session_id,
            "Session ID has {{}} in it: {}".format(self.marionette.session_id),
        )

    def test_windowless_false(self):
        self.marionette.delete_session()
        self.marionette.start_session({"moz:windowless": False})
        caps = self.marionette.session_capabilities
        self.assertFalse(caps["moz:windowless"])

    @unittest.skipUnless(sys.platform.startswith("darwin"), "Only supported on MacOS")
    def test_windowless_true(self):
        self.marionette.delete_session()
        self.marionette.start_session({"moz:windowless": True})
        caps = self.marionette.session_capabilities
        self.assertTrue(caps["moz:windowless"])


class TestCapabilityMatching(MarionetteTestCase):
    def setUp(self):
        MarionetteTestCase.setUp(self)
        self.browser_name = self.marionette.session_capabilities["browserName"]
        self.delete_session()

    def delete_session(self):
        if self.marionette.session is not None:
            self.marionette.delete_session()

    def test_accept_insecure_certs(self):
        for value in ["", 42, {}, []]:
            print(f"  type {type(value)}")
            with self.assertRaises(errors.SessionNotCreatedException):
                self.marionette.start_session({"acceptInsecureCerts": value})

        self.delete_session()
        self.marionette.start_session({"acceptInsecureCerts": True})
        self.assertTrue(self.marionette.session_capabilities["acceptInsecureCerts"])

    def test_page_load_strategy(self):
        for strategy in ["none", "eager", "normal"]:
            print(f"valid strategy {strategy}")
            self.delete_session()
            self.marionette.start_session({"pageLoadStrategy": strategy})
            self.assertEqual(
                self.marionette.session_capabilities["pageLoadStrategy"], strategy
            )

        self.delete_session()

        for value in ["", "EAGER", True, 42, {}, []]:
            print(f"invalid strategy {value}")
            with self.assertRaisesRegex(
                errors.SessionNotCreatedException, "InvalidArgumentError"
            ):
                self.marionette.start_session({"pageLoadStrategy": value})

    def test_set_window_rect(self):
        with self.assertRaisesRegex(
            errors.SessionNotCreatedException, "InvalidArgumentError"
        ):
            self.marionette.start_session({"setWindowRect": False})

    def test_timeouts(self):
        for value in ["", 2.5, {}, []]:
            print(f"  type {type(value)}")
            with self.assertRaises(errors.SessionNotCreatedException):
                self.marionette.start_session({"timeouts": {"pageLoad": value}})

        self.delete_session()

        timeouts = {"implicit": 0, "pageLoad": 2.0, "script": 2**53 - 1}
        self.marionette.start_session({"timeouts": timeouts})
        self.assertIn("timeouts", self.marionette.session_capabilities)
        self.assertDictEqual(self.marionette.session_capabilities["timeouts"], timeouts)
        self.assertDictEqual(
            self.marionette._send_message("WebDriver:GetTimeouts"), timeouts
        )

    def test_strict_file_interactability(self):
        for value in ["", 2.5, {}, []]:
            print(f"  type {type(value)}")
            with self.assertRaises(errors.SessionNotCreatedException):
                self.marionette.start_session({"strictFileInteractability": value})

        self.delete_session()

        self.marionette.start_session({"strictFileInteractability": True})
        self.assertIn("strictFileInteractability", self.marionette.session_capabilities)
        self.assertTrue(
            self.marionette.session_capabilities["strictFileInteractability"]
        )

        self.delete_session()

        self.marionette.start_session({"strictFileInteractability": False})
        self.assertIn("strictFileInteractability", self.marionette.session_capabilities)
        self.assertFalse(
            self.marionette.session_capabilities["strictFileInteractability"]
        )

    def test_unhandled_prompt_behavior_as_string(self):
        """WebDriver Classic (HTTP) style"""

        # Invalid values
        self.delete_session()
        for handler in ["", "ACCEPT", True, 42, []]:
            print(f"invalid unhandled prompt behavior {handler}")
            with self.assertRaisesRegex(
                errors.SessionNotCreatedException, "InvalidArgumentError"
            ):
                self.marionette.start_session({"unhandledPromptBehavior": handler})

        # Default value if capability is not requested when creating a new session.
        self.delete_session()
        self.marionette.start_session()
        self.assertEqual(
            self.marionette.session_capabilities["unhandledPromptBehavior"],
            "dismiss and notify",
        )

        for handler in PROMPT_HANDLERS:
            print(f"  value {handler}")
            self.delete_session()
            self.marionette.start_session({"unhandledPromptBehavior": handler})
            self.assertEqual(
                self.marionette.session_capabilities["unhandledPromptBehavior"],
                handler,
            )

    def test_unhandled_prompt_behavior_as_object(self):
        """WebDriver BiDi style"""

        # Invalid values
        self.delete_session()
        for handler in [{"foo": "accept"}, {"alert": "bar"}]:
            print(f"invalid unhandled prompt behavior {handler}")
            with self.assertRaisesRegex(
                errors.SessionNotCreatedException, "InvalidArgumentError"
            ):
                self.marionette.start_session({"unhandledPromptBehavior": handler})

        # Default value if capability is not requested when creating a new session.
        self.delete_session()
        self.marionette.start_session({"unhandledPromptBehavior": {}})
        self.assertEqual(
            self.marionette.session_capabilities["unhandledPromptBehavior"],
            {},
        )

        for prompt_type in PROMPT_TYPES:
            for handler in PROMPT_HANDLERS:
                value = {prompt_type: handler}
                print(f"  value {value}")
                self.delete_session()
                self.marionette.start_session({"unhandledPromptBehavior": value})
                self.assertEqual(
                    self.marionette.session_capabilities["unhandledPromptBehavior"],
                    value,
                )

    def test_web_socket_url(self):
        self.marionette.start_session({"webSocketUrl": True})
        # Remote Agent is not active by default
        self.assertNotIn("webSocketUrl", self.marionette.session_capabilities)

    def test_webauthn_extension_cred_blob(self):
        for value in ["", 42, {}, []]:
            print(f"  type {type(value)}")
            with self.assertRaises(errors.SessionNotCreatedException):
                self.marionette.start_session({"webauthn:extension:credBlob": value})

        self.delete_session()
        self.marionette.start_session({"webauthn:extension:credBlob": True})
        self.assertTrue(
            self.marionette.session_capabilities["webauthn:extension:credBlob"]
        )

    def test_webauthn_extension_large_blob(self):
        for value in ["", 42, {}, []]:
            print(f"  type {type(value)}")
            with self.assertRaises(errors.SessionNotCreatedException):
                self.marionette.start_session({"webauthn:extension:largeBlob": value})

        self.delete_session()
        self.marionette.start_session({"webauthn:extension:largeBlob": True})
        self.assertTrue(
            self.marionette.session_capabilities["webauthn:extension:largeBlob"]
        )

    def test_webauthn_extension_prf(self):
        for value in ["", 42, {}, []]:
            print(f"  type {type(value)}")
            with self.assertRaises(errors.SessionNotCreatedException):
                self.marionette.start_session({"webauthn:extension:prf": value})

        self.delete_session()
        self.marionette.start_session({"webauthn:extension:prf": True})
        self.assertTrue(self.marionette.session_capabilities["webauthn:extension:prf"])

    def test_webauthn_extension_uvm(self):
        for value in ["", 42, {}, []]:
            print(f"  type {type(value)}")
            with self.assertRaises(errors.SessionNotCreatedException):
                self.marionette.start_session({"webauthn:extension:uvm": value})

        self.delete_session()
        self.marionette.start_session({"webauthn:extension:uvm": True})
        self.assertTrue(self.marionette.session_capabilities["webauthn:extension:uvm"])

    def test_webauthn_virtual_authenticators(self):
        for value in ["", 42, {}, []]:
            print(f"  type {type(value)}")
            with self.assertRaises(errors.SessionNotCreatedException):
                self.marionette.start_session({"webauthn:virtualAuthenticators": value})

        self.delete_session()
        self.marionette.start_session({"webauthn:virtualAuthenticators": True})
        self.assertTrue(
            self.marionette.session_capabilities["webauthn:virtualAuthenticators"]
        )
