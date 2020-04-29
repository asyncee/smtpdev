FROM python:3.7-alpine

ENV SMTPDEV_WEB_HOST 0.0.0.0
ENV SMTPDEV_SMTP_HOST 0.0.0.0
ENV SMTPDEV_MAILDIR /smtpdev
WORKDIR /smtpdev
RUN pip install smtpdev

EXPOSE 2500 8080

CMD ["smtpdev"]
