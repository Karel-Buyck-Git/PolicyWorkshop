Fixture hierarchy — tests only

A deliberately tiny stand-in for `config/azure-domain-hierachy.md`, so the producer
phase tests are hermetic: an edit to the authored taxonomy must not break them, and a
bug in them must not be mistaken for a taxonomy change.

`Monitoring` is deliberately left out of this hierarchy — a policy in that category has to
land in the `undefined` catch-bucket, and that behaviour is asserted.

- Demoland

  - Tags
  - Storage

- Otherland

  - Security Center
