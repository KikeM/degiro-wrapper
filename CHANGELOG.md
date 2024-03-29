# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.6.5] - 24/07/22

ENH: Add versioneer

## [0.6.4] - 23/07/22

ENH: Compute tna and cfs with multicurrency positions

## [0.6.3] - 17/07/22

- CLN: Modify degiro describe entrypoint to be used 
to create portfolio definition.

## [0.6.2] - 17/07/22

- ENH: make download_position 100x faster
- ENH(report): avoid parse spaces when it reads a csv

Thanks to @mmngreco

## [0.6.1] - 24/06/22

CLN: Minor improvements after user-like usage:
  - Set `dpi` value for figure generation.
  - Simplify CLI command `check-missing-dates` to `check-dates`.
  - Refactor function names.

## [0.6.0] - 23/06/22

ENH: Create report MVP

## [0.5.0] - 23/06/22

ENH: Download and process transactions

## [0.4.0] - 23/06/22

ENH: Create Cashflows DB

## [0.3.1] - 23/06/22

BUG: Introduce one-day shift in "today" option
to download positions

## [0.3.0] - 22/06/22

ENH, TST: Create positions database

## [0.2.0] - 22/06/22

ENH: Add CLI:
  - BLD: Add requirements.txt
  - CLN: Folder reorganization
  - ENH: CLI to check missing position dates
  - ENH: CLI to download raw positions
