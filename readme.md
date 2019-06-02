# smtpdev

Asynchronous SMTP server for developers.

Currently this project is a work in progress.

## Installation

Just use pip:

```bash
pip install smtpdev
```

## Command line options description

```
$ smtpdev --help
Usage: smtpdev [OPTIONS]

Options:
  --smtp-host TEXT     Smtp server host.
  --smtp-port INTEGER  Smtp server port.
  --web-host TEXT      Web server host.
  --web-port INTEGER   Web server port.
  --develop            Run in developer mode.
  --debug              Whether to use debug loglevel.
  --maildir TEXT       Full path to emails directory, temporary directory if not set.
  --help               Show this message and exit.
```

## Development

### Installation

Clone repository and use following command to bootstrap
python environment and install package in editable mode.

```bash
make bootstrap
```

### Launching smtpdev

```bash
make run
```

### Running mypy

```bash
make check
```
