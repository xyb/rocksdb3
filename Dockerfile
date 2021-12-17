FROM quay.io/pypa/manylinux2014_x86_64

ENV PATH /root/.cargo/bin:$PATH
# Add all supported python versions
ENV PATH /opt/python/cp36-cp36m/bin/:/opt/python/cp37-cp37m/bin/:/opt/python/cp38-cp38/bin/:/opt/python/cp39-cp39/bin/:/opt/python/cp310-cp310/bin/:$PATH
# Otherwise `cargo new` errors
ENV USER root

RUN curl https://sh.rustup.rs -sSf | sh -s -- -y \
    && python3 -m pip install --no-cache-dir cffi maturin \
    && ln -s $(which maturin) /usr/bin/maturin \
    && mkdir /io

ENV LLVM_VERSION=3.9.1
RUN curl -o llvm.xz "https://releases.llvm.org/${LLVM_VERSION}/clang+llvm-${LLVM_VERSION}-x86_64-linux-gnu-ubuntu-14.04.tar.xz" \
    && tar -xf llvm.xz -C /usr/local/ --strip-components=1 \
    && rm -rf llvm.xz

WORKDIR /io

ENTRYPOINT ["/usr/bin/maturin"]
