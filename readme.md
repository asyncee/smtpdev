# smtpdev

Asynchronous SMTP server for developers.

## Installation

Just use pip:

```bash
pip install smtpdev
```

## Launching

You can launch smtpdev by issuing `smtpdev` command. All parameters have pre-set defaults.

## Command line options description

```
$ smtpdev --help
Usage: smtpdev [OPTIONS]

Options:
  --smtp-host TEXT     Smtp server host (default localhost).
  --smtp-port INTEGER  Smtp server port (default 2500).
  --web-host TEXT      Web server host (default localhost).
  --web-port INTEGER   Web server port (default 8080).
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
