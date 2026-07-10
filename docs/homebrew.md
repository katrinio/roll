# Homebrew tap

`roll` is a good fit for a personal Homebrew tap before aiming at `homebrew/core`.

## Why a tap first

- no central review queue;
- easier iteration on formula changes;
- suitable for niche CLI tools;
- users can still install with a single `brew install owner/tap/roll`.

## Expected repository layout

Create a separate repository named `homebrew-tap`:

```text
homebrew-tap/
└── Formula/
    └── roll.rb
```

Use [`packaging/homebrew/roll.rb`](../packaging/homebrew/roll.rb) as the starting point.

## Install flow

```bash
brew tap katrinio/tap
brew install roll
```

Or in one command:

```bash
brew install katrinio/tap/roll
```

## Release checklist

1. Push a tagged release such as `v0.8.0`.
2. Wait for the `package` GitHub Actions workflow to build `sdist` and wheel artifacts for that tag.
3. Compute the GitHub tag tarball checksum for that exact release:

```bash
curl -L -o /tmp/roll-v0.8.0.tar.gz \
  https://github.com/katrinio/roll/archive/refs/tags/v0.8.0.tar.gz
shasum -a 256 /tmp/roll-v0.8.0.tar.gz
```

4. Copy [`packaging/homebrew/roll.rb`](../packaging/homebrew/roll.rb) into the tap as `Formula/roll.rb`.
5. Update `url` and top-level `sha256` in the formula.
6. Fill Python dependency resource checksums. If Homebrew developer commands are available, run:

```bash
brew update-python-resources Formula/roll.rb
```

7. Run `brew install --build-from-source ./Formula/roll.rb`.
8. Run `brew test roll`.

## Notes for `roll`

- `rl update` intentionally does not self-update. Homebrew users should use `brew upgrade roll`.
- package versioning is configured to work from git archives used by tagged source tarballs.
- a meaningful `brew test` should initialize a temporary archive and verify that `.roll` was created.
