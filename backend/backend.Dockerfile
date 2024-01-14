FROM nvcr.io/nvidia/cuda:11.6.2-cudnn8-devel-ubuntu20.04

ENV DEBIAN_FRONTEND=noninteractive \
	LC_ALL=en_US.UTF-8

RUN apt-get update && \
	apt-get install -y \
	locales \
	python3.9-dev \
	python3-pip \
	ipython3 \
	git

RUN locale-gen en_US.UTF-8 && \
	update-locale && \
	update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 10 && \
	update-alternatives --install /usr/bin/python python /usr/bin/python3 10 && \
	update-alternatives --install /usr/bin/ipython ipython /usr/bin/ipython3 10 && \
	update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 10 && \
	ln -s /usr/local/cuda/lib64/libcusolver.so.11 /usr/local/cuda/lib64/libcusolver.so.10 && \
	pip --no-cache-dir install --upgrade pip

ARG TORCH_VER="1.13.0" \
    TORCH_VISION_VER="0.14.0"

ARG CUDA_VER="cu116"

RUN pip --no-cache-dir install \
    torch==${TORCH_VER}+${CUDA_VER} \
    torchvision==${TORCH_VISION_VER}+${CUDA_VER} \
    -f "https://download.pytorch.org/whl/${CUDA_VER}/torch_stable.html"

RUN apt-get update -y
RUN apt-get -y install default-mysql-client
RUN apt-get install libjpeg62
RUN apt-get install r-base -y

# detectron env
RUN apt-get install ffmpeg -y
RUN pip install 'git+https://github.com/facebookresearch/detectron2.git'

# other env
COPY ./requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt
RUN rm /tmp/requirements.txt

RUN apt-get update && apt-get install -y docker.io
RUN pip3 install docker


# COPY ./backend/ /root/backend/
# WORKDIR /root/backend/

CMD ["/bin/bash"]
