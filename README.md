<h1 align="center">
    <strong>depends</strong>
</h1>
<p align="center">
    <a href="https://github.com/dmtrs/depends" target="_blank">
        <img src="https://img.shields.io/github/last-commit/dmtrs/depends" alt="Latest Commit">
    </a>
        <img src="https://img.shields.io/github/workflow/status/dmtrs/depends/Test">
        <img src="https://img.shields.io/codecov/c/github/dmtrs/depends">
    <br />
    <a href="https://pypi.org/project/depends" target="_blank">
        <img src="https://img.shields.io/pypi/v/depends" alt="Package version">
    </a>
    <img src="https://img.shields.io/pypi/pyversions/depends">
    <img src="https://img.shields.io/github/license/dmtrs/depends">
</p>


## Installation

``` bash
pip install depends
```

## Development

```bash
docker build -t depends .
```

```bash
docker run --rm -v $(pwd):/usr/src/app depends scripts/test
```


## License

This project is licensed under the terms of the MIT license.
