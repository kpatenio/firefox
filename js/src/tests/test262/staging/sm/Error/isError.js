// |reftest| shell-option(--enable-error-iserror) skip-if(!Error.isError||!xulRuntime.shell) -- Error.isError is not enabled unconditionally, requires shell-options
// Copyright (C) 2025 Mozilla Corporation. All rights reserved.
// This code is governed by the BSD license found in the LICENSE file.

/*---
features:
  - Error.isError
includes: [sm/non262.js, sm/non262-shell.js]
flags:
  - noStrict
description: |
  pending
esid: pending
---*/

// Test non-object input should return false
assert.sameValue(Error.isError(null), false);
assert.sameValue(Error.isError(undefined), false);
assert.sameValue(Error.isError(123), false);
assert.sameValue(Error.isError("string"), false);

// Test plain objects should return false
assert.sameValue(Error.isError({}), false);
assert.sameValue(Error.isError(new Object()), false);

// Test various error objects should return true
assert.sameValue(Error.isError(new Error()), true);
assert.sameValue(Error.isError(new TypeError()), true);
assert.sameValue(Error.isError(new RangeError()), true);


reportCompare(0, 0);
