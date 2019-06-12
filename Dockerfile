FROM python:3.7-alpine as base

FROM base as builder

WORKDIR /install
COPY requirements.txt /
RUN pip install -r /requirements.txt --install-option="--prefix=/install"
RUN pip install smtpdev --install-option="--prefix=/install" --no-deps

FROM base

ENV SMTPDEV_WEB_HOST 0.0.0.0
ENV SMTPDEV_SMTP_HOST 0.0.0.0
ENV SMTPDEV_MAILDIR /smtpdev
WORKDIR /smtpdev
RUN adduser smtpd -D -h /smtpdev
USER smtpd:smtpd
COPY --from=builder /install /usr/local

EXPOSE 2500 8080

CMD ["/usr/local/bin/smtpdev"]