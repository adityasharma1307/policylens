FROM python:3.11-slim

# Headless Chrome is needed only to render the policy brief PDF (report/render_brief.py
# uses --print-to-pdf rather than pandoc/LaTeX, neither of which is available here).
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    make \
    && rm -rf /var/lib/apt/lists/*

ENV POLICYLENS_CHROME_BIN=/usr/bin/chromium

WORKDIR /app

COPY pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir -e .

COPY . .

CMD ["make", "all"]
