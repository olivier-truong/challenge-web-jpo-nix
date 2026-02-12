FROM python:3.12-alpine AS builder
RUN apk update && apk add --no-cache gcc musl-dev linux-headers
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
FROM python:3.12-alpine AS final
RUN adduser -D ctfuser
WORKDIR /home/ctfuser/app
COPY --from=builder /opt/venv /opt/venv
RUN rm -rf /var/cache/apk/*
ENV PATH="/opt/venv/bin:$PATH"
COPY app/ .
COPY FLAGS/flag.txt /var/.flag.txt
RUN chown -R root:root /home/ctfuser/app /var/.flag.txt
EXPOSE 8080

USER ctfuser
CMD ["python", "app.py"]
