FROM quay.io/pypa/manylinux2014_x86_64

ENV PATH /root/.cargo/bin:$PATH
# Add all supported python versions
ENV PATH /opt/python/cp35-cp35m/bin/:/opt/python/cp36-cp36m/bin/:/opt/python/cp37-cp37m/bin/:/opt/python/cp38-cp38/bin/:$PATH
# Otherwise `cargo new` errors
ENV USER root

RUN curl https://sh.rustup.rs -sSf | sh -s -- -y \
    && python3 -m pip install --no-cache-dir cffi maturin \
    && ln -s $(which maturin) /usr/bin/maturin \
    && mkdir /io

RUN curl -o llvm.xz 'https://releases.llvm.org/3.8.0/clang+llvm-3.8.0-linux-x86_64-centos6.tar.xz' \
    && tar -xf llvm.xz \
    && cd clang+llvm-3.8.0-linux-x86_64-centos6/ \
    && cp -r * /usr/local/ \
    && cd ../ \
    && rm -rf llvm.xz clang+llvm-3.8.0-linux-x86_64-centos6/

WORKDIR /io

ENTRYPOINT ["/usr/bin/maturin"]
