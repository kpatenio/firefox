/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

let gParams;

const { AppConstants } = ChromeUtils.importESModule(
  "resource://gre/modules/AppConstants.sys.mjs"
);

function init() {
  /*
   * The C++ code passes a dialog param block using its integers as in and out
   * arguments for this UI. The following are the uses of the integers:
   *
   *  0: A set of flags from nsIToolkitProfileService.downgradeUIFlags.
   *  1: A return argument, one of nsIToolkitProfileService.downgradeUIChoice.
   */
  gParams = window.arguments[0].QueryInterface(Ci.nsIDialogParamBlock);
  let hasSync =
    AppConstants.MOZ_SERVICES_SYNC &&
    gParams.GetInt(0) & Ci.nsIToolkitProfileService.hasSync;

  document.getElementById("sync").hidden = !hasSync;
  document.getElementById("nosync").hidden = hasSync;

  document.addEventListener("dialogextra1", createProfile);
  document.addEventListener("dialogaccept", quit);
  document.addEventListener("dialogcancel", quit);
}

function quit() {
  gParams.SetInt(1, Ci.nsIToolkitProfileService.quit);
}

function createProfile() {
  gParams.SetInt(1, Ci.nsIToolkitProfileService.createNewProfile);
  window.close();
}

window.addEventListener("load", () => init());
