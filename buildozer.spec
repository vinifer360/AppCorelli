name: CI
on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-20.04

    steps:
      - uses: actions/checkout@v2

      - name: Set up Python 3.9
        uses: actions/setup-python@v2
        with:
          python-version: 3.9

      - name: Install Buildozer and Cython
        run: |
          pip install --upgrade buildozer cython

      - name: Get Date
        id: get-date
        run: |
          echo "::set-output name=date::$(/bin/date -u "+%Y%m%d")"

      - name: Cache Buildozer global directory
        uses: actions/cache@v2
        with:
          path: .buildozer_global
          key: buildozer-global-${{ hashFiles('buildozer.spec') }}

      - uses: actions/cache@v2
        with:
          path: .buildozer
          key: ${{ runner.os }}-${{ steps.get-date.outputs.date }}-${{ hashFiles('buildozer.spec') }}

      - name: Build with Buildozer
        uses: ArtemSBulgakov/buildozer-action@v1
        id: buildozer
        with:
          command: buildozer android debug
          buildozer_version: stable

      - name: Upload artifacts
        uses: actions/upload-artifact@v2
        with:
          name: package
          path: ${{ steps.buildozer.outputs.filename }}
