# smtpdev

Asynchronous SMTP server for developers.

Currently this project is a work in progress.

## Installation for local development

```bash
make bootstrap
```

## Running mypy

```bash
make check
```

## Launching smtpdev

```bash
make run
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
