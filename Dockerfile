FROM python:3.6

RUN git clone https://github.com/RustyPanda/shared-astro-utilities.git ../shared_astro_utilities
RUN pip install -r requirements.txt