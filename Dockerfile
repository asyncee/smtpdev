FROM python:3.7-alpine

ENV SMTPDEV_WEB_HOST 0.0.0.0
ENV SMTPDEV_SMTP_HOST 0.0.0.0
ENV SMTPDEV_MAILDIR /smtpdev
WORKDIR /smtpdev
RUN pip install smtpdev==0.2.8

EXPOSE 2500 8080

CMD ["smtpdev"]
