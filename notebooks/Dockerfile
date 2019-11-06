FROM python:3.7.4
RUN pip3 install -U \
  jupyter papermill \
  pandas numpy scipy matplotlib \
  joblib requests \
  tensorflow \
  pip
RUN python -m ipykernel install --name 3.7.4

ADD run.ipynb /

ENTRYPOINT [ "jupyter", "nbconvert", "/run.ipynb", "/out/run.ipynb" ]
