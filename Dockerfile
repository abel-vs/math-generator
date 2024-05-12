FROM python:3.9.8

WORKDIR /app

RUN apt update
RUN apt -y upgrade
RUN apt install -y libcairo2-dev
RUN apt install -y ffmpeg
RUN apt install -y texlive texlive-latex-extra texlive-fonts-extra texlive-latex-recommended texlive-science texlive-fonts-extra
RUN apt install -y libpango1.0-dev pkg-config

RUN pip install poetry

COPY pyproject.toml /app/pyproject.toml

RUN poetry install

COPY src /app/src

EXPOSE 8501

RUN mkdir videos

CMD ["poetry", "run", "streamlit", "run", "src/main.py"]