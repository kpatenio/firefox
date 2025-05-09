// |reftest| shell-option(--enable-temporal) skip-if(!this.hasOwnProperty('Temporal')||!xulRuntime.shell) -- Temporal is not enabled unconditionally, requires shell-options
// Copyright (C) 2022 Igalia, S.L. All rights reserved.
// This code is governed by the BSD license found in the LICENSE file.

/*---
esid: sec-temporal.duration.prototype.round
description: A number cannot be used in place of a relativeTo
features: [Temporal]
---*/

const instance = new Temporal.Duration(1, 0, 0, 0, 24);

const numbers = [
  1,
  20191101,
  -20191101,
  1234567890,
];

for (const relativeTo of numbers) {
  assert.throws(
    TypeError,
    () => instance.round({ largestUnit: "years", relativeTo }),
    `A number (${relativeTo}) is not a valid ISO string for relativeTo`
  );
}

reportCompare(0, 0);
